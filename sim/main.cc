/*
 * Copyright (C) 2017 CAMELab
 *
 * This file is part of SimpleSSD.
 *
 * SimpleSSD is free software: you can redistribute it and/or modify
 * it under the terms of the GNU General Public License as published by
 * the Free Software Foundation, either version 3 of the License, or
 * (at your option) any later version.
 *
 * SimpleSSD is distributed in the hope that it will be useful,
 * but WITHOUT ANY WARRANTY; without even the implied warranty of
 * MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
 * GNU General Public License for more details.
 *
 * You should have received a copy of the GNU General Public License
 * along with SimpleSSD.  If not, see <http://www.gnu.org/licenses/>.
 */

#include <filesystem>
#include <fstream>
#include <iostream>
#include <memory>
#include <thread>

#include "bil/entry.hh"
#include "igl/request/request_generator.hh"
#include "igl/trace/trace_replayer.hh"
#include "sil/none/none.hh"
#include "sil/nvme/nvme.hh"
#include "sim/engine.hh"
#include "sim/signal.hh"
#include "simplessd/util/simplessd.hh"
#include "util/print.hh"

namespace fs = std::filesystem;

// Global objects
Engine engine;
ConfigReader simConfig;
BIL::DriverInterface *pInterface = nullptr;
BIL::BlockIOEntry *pBIOEntry = nullptr;
IGL::IOGenerator *pIOGen = nullptr;
std::ostream *pLog = nullptr;
std::ostream *pDebugLog = nullptr;
std::ostream *pLatencyFile = nullptr;
unique_ptr<std::ofstream> pStatisticsFile;
std::thread *pThread = nullptr;
std::mutex killLock;
SimpleSSD::Event statEvent;
std::vector<SimpleSSD::Stats> statList;
std::ofstream logOut;
std::ofstream debugLogOut;
std::ofstream latencyFile;

// Declaration
void cleanup(int);
void statistics(uint64_t);
void threadFunc(int);

void joinPath(std::string &lhs, std::string &rhs) {
  if (rhs.front() == '/') {
    // Assume absolute path
    lhs = rhs;
  }
  else if (lhs.back() == '/') {
    lhs += rhs;
  }
  else {
    lhs += '/';
    lhs += rhs;
  }
}

void CreatePathIfNotExists(std::string path) {
  fs::path p(path);
  if (!fs::is_directory(p.parent_path()) || !fs::exists(p.parent_path())) {
    fs::create_directories(p.parent_path());
  }
}

int main(int argc, char *argv[]) {
  std::cout << "SimpleSSD Standalone v2.0" << std::endl;
  std::cout << "Input: ";
  for (int i = 0; i < argc; ++i) {
	  std::cout << argv[i] << " \n"[i + 1 == argc];
  }

  // Check argument
  if (argc != 4) {
    std::cerr << " Invalid number of argument!" << std::endl;
    std::cerr << "  Usage: simplessd-standalone <Simulation configuration "
                 "file> <SimpleSSD configuration file> <Output directory>"
              << std::endl;

    return 1;
  }

  // Install signal handler
  installSignalHandler(cleanup);

  // Read simulation config file
  if (!simConfig.init(argv[1])) {
    std::cerr << " Failed to open simulation configuration file!" << std::endl;

    return 2;
  }

  // Log setting
  bool noLogPrintOnScreen = true;

  std::string logPath = simConfig.readString(CONFIG_GLOBAL, GLOBAL_LOG_FILE);
  std::string debugLogPath =
      simConfig.readString(CONFIG_GLOBAL, GLOBAL_DEBUG_LOG_FILE);
  std::string latencyLogPath =
      simConfig.readString(CONFIG_GLOBAL, GLOBAL_LATENCY_LOG_FILE);
  std::string statisticsLogPath = "stats.txt";

  if (logPath.compare("STDOUT") == 0) {
    noLogPrintOnScreen = false;
    pLog = &std::cout;
  }
  else if (logPath.compare("STDERR") == 0) {
    noLogPrintOnScreen = false;
    pLog = &std::cerr;
  }
  else if (logPath.length() != 0) {
    std::string full(argv[3]);

    joinPath(full, logPath);
    CreatePathIfNotExists(full);
    logOut.open(full);

    if (!logOut.is_open()) {
      std::cerr << " Failed to open log file: " << full << std::endl;

      return 3;
    }

    pLog = &logOut;
  }

  if (debugLogPath.compare("STDOUT") == 0) {
    noLogPrintOnScreen = false;
    pDebugLog = &std::cout;
  }
  else if (debugLogPath.compare("STDERR") == 0) {
    noLogPrintOnScreen = false;
    pDebugLog = &std::cerr;
  }
  else if (debugLogPath.length() != 0) {
    std::string full(argv[3]);

    joinPath(full, debugLogPath);
    CreatePathIfNotExists(full);
    debugLogOut.open(full);

    if (!debugLogOut.is_open()) {
      std::cerr << " Failed to open log file: " << full << std::endl;

      return 3;
    }

    pDebugLog = &debugLogOut;
  }

  if (latencyLogPath.length() != 0) {
    std::string full(argv[3]);

    joinPath(full, latencyLogPath);
    CreatePathIfNotExists(full);
    latencyFile.open(full);

    if (!latencyFile.is_open()) {
      std::cerr << " Failed to open log file: " << full << std::endl;

      return 3;
    }

    pLatencyFile = &latencyFile;
  }

  if (statisticsLogPath.length() != 0) {
    std::string full(argv[3]);

    joinPath(full, statisticsLogPath);
    CreatePathIfNotExists(full);
    pStatisticsFile = make_unique<std::ofstream>(full);

    if (!pStatisticsFile->is_open()) {
      std::cerr << " Failed to open statistics file: " << full << std::endl;

      return 3;
    }
  }

  // Initialize SimpleSSD
  auto ssdConfig = initSimpleSSDEngine(&engine, pDebugLog, pDebugLog, argv[2]);
  SIL::NVMe::Driver* nvme_driver = nullptr;

  // Create Driver
  switch (simConfig.readUint(CONFIG_GLOBAL, GLOBAL_INTERFACE)) {
    case INTERFACE_NONE:
      pInterface = new SIL::None::Driver(engine, ssdConfig);

      break;
    case INTERFACE_NVME:
	  nvme_driver = new SIL::NVMe::Driver(engine, ssdConfig);
      pInterface = nvme_driver;

      break;
    default:
      std::cerr << " Undefined interface specified." << std::endl;

      return 4;
  }

  // Create Block I/O Layer
  pBIOEntry =
      new BIL::BlockIOEntry(simConfig, engine, pInterface, pLatencyFile);
  if(nvme_driver)
	  nvme_driver->pBio = pBIOEntry;

  std::function<void()> endCallback = []() {
    // If stat printout is scheduled, delete it
    if (simConfig.readUint(CONFIG_GLOBAL, GLOBAL_LOG_PERIOD) > 0) {
      engine.descheduleEvent(statEvent);
    }

    // Stop simulation
    engine.stopEngine();
  };

  // Create I/O generator
  switch (simConfig.readUint(CONFIG_GLOBAL, GLOBAL_SIM_MODE)) {
    case MODE_REQUEST_GENERATOR:
      pIOGen =
          new IGL::RequestGenerator(engine, *pBIOEntry, endCallback, simConfig);

      break;
    case MODE_TRACE_REPLAYER:
      pIOGen =
          new IGL::TraceReplayer(engine, *pBIOEntry, endCallback, simConfig);

      break;
    default:
      std::cerr << " Undefined simulation mode specified." << std::endl;

      cleanup(0);

      return 5;
  }

  std::function<void()> beginCallback = []() {
    uint64_t bytesize;
    uint32_t bs;

    pInterface->getInfo(bytesize, bs);
    pIOGen->init(bytesize, bs);
    pIOGen->begin(); // mjo: Reads a trace file
  };

  // Insert stat event
  pInterface->initStats(statList);

  // mjo: Log statistics periodically
  if (simConfig.readUint(CONFIG_GLOBAL, GLOBAL_LOG_PERIOD) > 0) {
    statEvent = engine.allocateEvent([](uint64_t tick) {
      statistics(tick);

      engine.scheduleEvent(
          statEvent,
          tick + simConfig.readUint(CONFIG_GLOBAL, GLOBAL_LOG_PERIOD) *
                     1000000000ULL);
    });
    engine.scheduleEvent(
        statEvent,
        simConfig.readUint(CONFIG_GLOBAL, GLOBAL_LOG_PERIOD) * 1000000000ULL);
  }

  // Do Simulation
  std::cout << "********** Begin of simulation **********" << std::endl;

  // mjo: Register a callback which runs traces
  // arrow means registering a function to an event queue.
  // init -> init0 -> init1 -> init2 -> init3 -> init4 -> init5
  // Finally init5 directly calls beginFunction, same to beginCallBack on above.
  // Since beginCallBack invokes TraceReplayer::begin, TraceReplayer::submitIO, TraceReplayer::handleNextLine sequentially.
  // In other words, it firstly registers a code to invoke TraceReplayer::submitIO.
  pInterface->init(beginCallback);

  if (noLogPrintOnScreen) {
    int period = (int)simConfig.readUint(CONFIG_GLOBAL, GLOBAL_PROGRESS_PERIOD);

    if (period > 0) {
      pThread = new std::thread(threadFunc, period);
    }
  }

  // ##### How does it repeatedly read traces? #####
  //
  // As I mentioned above, pInterface->init sets TraceReplayer::submitIO.
  // handleNextLine, invoked by submitIO, invokes engine.scheduleEvent and it inserts submitIO job to the queue.


  while (engine.doNextEvent())
    ;

  cleanup(0);

  return 0;
}

void cleanup(int) {
  uint64_t tick;

  killLock.lock();

  tick = engine.getCurrentTick();

  if (tick == 0) {
    // Exit program
    exit(0);
  }

  // Print last statistics
  statistics(tick);

  // Erase progress
  printf("\33[2K                                                           \r");

  releaseSimpleSSDEngine();

  pIOGen->printStats(std::cout);
  engine.printStats(std::cout);
  if (pStatisticsFile.get()) {
    pIOGen->printStats(*pStatisticsFile);
    engine.printStats(*pStatisticsFile);
  }

  // Cleanup all here
  delete pInterface;
  delete pIOGen;

  if (pThread) {
    pThread->join();

    delete pThread;
  }

  delete pBIOEntry;  // Used by progress thread

  if (logOut.is_open()) {
    logOut.close();
  }
  if (debugLogOut.is_open()) {
    debugLogOut.close();
  }

  std::cout << "End of simulation @ tick " << tick << std::endl;

  // Exit program
  exit(0);
}

void statistics(uint64_t tick) {
  if (pLog == nullptr) {
    return;
  }

  std::ostream &out = *pLog;
  std::vector<double> stat;
  uint64_t count = 0;

  pInterface->getStats(stat);

  count = statList.size();

  if (count != stat.size()) {
    std::cerr << " Stat list length mismatch" << std::endl;

    std::terminate();
  }

  out << "Periodic log printout @ tick " << tick << std::endl;

  for (uint64_t i = 0; i < count; i++) {
    print(out, statList[i].name, 40);
    out << "\t";
    print(out, stat[i], 20);
    out << "\t" << statList[i].desc << std::endl;
  }

  out << "End of log @ tick " << tick << std::endl;
}

void threadFunc(int tick) {
  uint64_t current;
  uint64_t old = 0;
  float progress;
  auto duration = std::chrono::seconds(tick);
  //BIL::Progress data;

  while (true) {
    std::this_thread::sleep_for(duration);

    if (killLock.try_lock()) {
      killLock.unlock();
    }
    else {
      break;
    }

    engine.getStat(current);
    pIOGen->getProgress(progress);
    //pBIOEntry->getProgress(data);

    printf("\33[2K*** Progress: %.2f%% (%lf ops)\r",
           progress * 100.f, (double)(current - old) / tick);
    fflush(stdout);

    old = current;
  }
}
