/* -*- Mode:C++; c-file-style:"gnu"; indent-tabs-mode:nil; -*- */
/**
 * Copyright (c) 2015 Christian Kreuzberger and Daniel Posch, Alpen-Adria-University
 * Klagenfurt
 *
 * This file is part of amus-ndnSIM, based on ndnSIM. See AUTHORS for complete list of
 * authors and contributors.
 *
 * amus-ndnSIM and ndnSIM are free software: you can redistribute it and/or modify it
 * under the terms of the GNU General Public License as published by the Free Software
 * Foundation, either version 3 of the License, or (at your option) any later version.
 *
 * amus-ndnSIM is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY;
 * without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR
 * PURPOSE.  See the GNU General Public License for more details.
 *
 * You should have received a copy of the GNU General Public License along with
 * amus-ndnSIM, e.g., in COPYING.md file.  If not, see <http://www.gnu.org/licenses/>.
 **/

// ndn-simple.cpp

#include "ns3/core-module.h"
#include "ns3/network-module.h"
#include "ns3/point-to-point-module.h"
#include "ns3/point-to-point-layout-module.h"

#include "ns3/ndnSIM/apps/ndn-app.hpp"

#include "ns3/ndnSIM-module.h"
#include "ns3/ndnSIM/helper/ndn-brite-topology-helper.hpp"
#include "ns3/ndnSIM/utils/tracers/ndn-dashplayer-tracer.hpp"


#include <boost/filesystem.hpp>

namespace ns3 {


void
FileDownloadedTrace(Ptr<ns3::ndn::App> app, shared_ptr<const ndn::Name> interestName, double downloadSpeed, long milliSeconds)
{
  std::cout << "Trace: File finished downloading: " << Simulator::Now().GetMilliSeconds () << " "<< *interestName <<
     " Download Speed: " << downloadSpeed/1000.0 << " Kilobit/s in " << milliSeconds << " ms" << std::endl;
}

void
FileDownloadedManifestTrace(Ptr<ns3::ndn::App> app, shared_ptr<const ndn::Name> interestName, long fileSize)
{
  std::cout << "Trace: Manifest received: " << Simulator::Now().GetMilliSeconds () <<" "<< *interestName << " File Size: " << fileSize << std::endl;
}

void
FileDownloadStartedTrace(Ptr<ns3::ndn::App> app, shared_ptr<const ndn::Name> interestName)
{
  std::cout << "Trace: File started downloading: " << Simulator::Now().GetMilliSeconds () <<" "<< *interestName << std::endl;
}


int
main(int argc, char* argv[])
{
  std::string confFile = "brite.conf";
  int numClients = 100;
  int numServers = 5;
  std::string routingStrategy = "bestroute";
  std::string cachingStrategy = "nocache";
  std::string numCacheEntries = "1000";
  std::string outputFolder = "output";
  std::string dashAdaptationLogic = "DASHJS";
  std::string serverType = "fake";

  // Read optional command-line parameters (e.g., enable visualizer with ./waf --run=<> --visualize
  CommandLine cmd;
  cmd.AddValue ("briteConfFile", "BRITE configuration file", confFile);
  cmd.AddValue ("fwStrategy", "Forwarding Strategy (bestroute, broadcast, NCC, SAF)", routingStrategy);
  cmd.AddValue ("csStrategy", "Caching/content store Strategy (nocache, LRU, LFU, FIFO)", cachingStrategy);
  cmd.AddValue ("cacheEntries", "Number of maximum cache entries (integer)", numCacheEntries);
  cmd.AddValue ("outputFolder", "Where to put trace files", outputFolder);
  cmd.AddValue ("adaptationLogic", "DASH Adaptation Logic: AlwaysLowest, Rate, RateBuffer, DASHJS", dashAdaptationLogic);
  cmd.AddValue ("serverType", "Select Server Type (fake or real)", serverType);

  cmd.Parse(argc, argv);


  if (dashAdaptationLogic == "DASHJS")
  {
    dashAdaptationLogic = "dash::player::DASHJSAdaptationLogic";
  } else if (dashAdaptationLogic == "Rate")
  {
    dashAdaptationLogic = "dash::player::RateBasedAdaptationLogic";
  } else if (dashAdaptationLogic == "RateBuffer")
  {
    dashAdaptationLogic = "dash::player::RateAndBufferBasedAdaptationLogic";
  } else if (dashAdaptationLogic == "AlwaysLowest")
  {
    dashAdaptationLogic = "dash::player::AlwaysLowestAdaptationLogic";
  } else { // default
    dashAdaptationLogic = "dash::player::AlwaysLowestAdaptationLogic";
  }

  // Create NDN Stack
  ndn::StackHelper ndnHelper;

  // Create Brite Topology Helper
  ndn::NDNBriteTopologyHelper bth (confFile);
  bth.AssignStreams (3);
  // tell the topology helper to build the topology
  bth.BuildBriteTopology ();

  // Separate clients, servers and routers
  NodeContainer client;
  NodeContainer server;
  NodeContainer router;
  NodeContainer leafnodes;

  uint32_t sumLeafNodes = 0;


  for (uint32_t i = 0; i < bth.GetNAs(); i++)
  {
    std::cout << "Number of nodes for AS: " << bth.GetNNodesForAs(i) << ", non leaf nodes: " << bth.GetNNonLeafNodesForAs(i) << std::endl;
    for(int node=0; node < bth.GetNNonLeafNodesForAs(i); node++)
    {
      std::cout << "Node " << node << " has " << bth.GetNonLeafNodeForAs(i,node)->GetNDevices() << " devices " << std::endl;
      //container.Add (briteHelper->GetNodeForAs (ASnumber,node));
      router.Add(bth.GetNonLeafNodeForAs(i,node));
    }
  }

  for (uint32_t i = 0; i < bth.GetNAs(); i++)
  {
    uint32_t numLeafNodes = bth.GetNLeafNodesForAs(i);

    std::cout << "AS " << i << " has " << numLeafNodes << "leaf nodes! " << std::endl;

    for (uint32_t j= 0; j < numLeafNodes; j++)
    {
      leafnodes.Add(bth.GetLeafNodeForAs(i,j));
    }

    sumLeafNodes += numLeafNodes;
  }

  UniformVariable randInt(0,1);

  client.Create(numClients);
  server.Create(numServers);

  PointToPointHelper p2pClient;
  p2pClient.SetChannelAttribute ("Delay", StringValue ("2ms"));
  p2pClient.SetDeviceAttribute ("DataRate", StringValue ("5Mbps"));
  p2pClient.SetQueue("ns3::DropTailQueue","MaxPackets",UintegerValue(50));


  PointToPointHelper p2pServer;
  p2pServer.SetChannelAttribute ("Delay", StringValue ("2ms"));
  p2pServer.SetDeviceAttribute ("DataRate", StringValue ("30Mbps"));
  p2pServer.SetQueue("ns3::DropTailQueue","MaxPackets",UintegerValue(100));

  std::cout << "Total Number of leaf nodes: " << sumLeafNodes << std::endl;
  // distribute leaf nodes for clients and servers
  for (uint32_t i = 0; i < numClients; i++)
  {
    // get a random leaf node
    uint32_t randomNumber = randInt.GetInteger(0,sumLeafNodes-1);
    ns3::Ptr<ns3::Node> randomNode = leafnodes.Get(randomNumber);


    p2pClient.Install(randomNode, client.Get(i));
  }

  std::cout << "Connected clients!" << std::endl;

  for (uint32_t i = 0; i < numServers; i++)
  {
    // get a random leaf node
    uint32_t randomNumber = randInt.GetInteger(0,sumLeafNodes-1);
    ns3::Ptr<ns3::Node> randomNode = leafnodes.Get(randomNumber);


    p2pServer.Install(randomNode, server.Get(i));
  }


  std::cout << "Connected servers!" << std::endl;




  ndnHelper.setCsSize(0); // use old content store

  // clients do not really need a large content store, but it could be beneficial to give them some
  ndnHelper.SetOldContentStore ("ns3::ndn::cs::Fifo","MaxSize", "100");
  ndnHelper.Install (client);


  // servers do not need a content store at all, they have an app to do that
  ndnHelper.SetOldContentStore ("ns3::ndn::cs::Fifo","MaxSize", "1");
  ndnHelper.Install (server);

  // what really needs a content store is the routers and leafnodes (which is where the clients are connected)

  if (cachingStrategy == "nocache")
  {
    std::cout << "Setting cache of routers to no-cache" << std::endl;
    ndnHelper.setCsSize(1); // disable content store
  } else if (cachingStrategy == "LRU")
  {
    std::cout << "Using LRU caching strategies on routers " << std::endl;
    ndnHelper.setCsSize(0); // use old content store
    ndnHelper.SetOldContentStore ("ns3::ndn::cs::Lru","MaxSize", numCacheEntries);
  } else if (cachingStrategy == "LFU")
  {
    std::cout << "Using LFU caching strategies on routers " << std::endl;
    ndnHelper.setCsSize(0); // use old content store
    ndnHelper.SetOldContentStore ("ns3::ndn::cs::Lfu","MaxSize", numCacheEntries);
  } else if (cachingStrategy == "FIFO")
  {
    std::cout << "Using FIFO caching strategies on routers " << std::endl;
    ndnHelper.setCsSize(0); // use old content store
    ndnHelper.SetOldContentStore ("ns3::ndn::cs::Fifo","MaxSize", numCacheEntries);
  }

  ndnHelper.Install(router);
  ndnHelper.Install (leafnodes);

  //ndnHelper.SetDefaultRoutes(true);
  std::string m_actualRoutingStrategy = "";
  // Choosing forwarding strategy
  if (routingStrategy == "bestroute")
  {
    fprintf(stderr, "Installing bestroute strategy...\n");
    m_actualRoutingStrategy = "/localhost/nfd/strategy/best-route";
  } else if (routingStrategy == "broadcast")
  {
    fprintf(stderr, "Installing broadcast strategy...\n");
    m_actualRoutingStrategy = "/localhost/nfd/strategy/broadcast";
  } else if (routingStrategy == "SAF")
  {
    fprintf(stderr, "Installing SAF startegy...\n");
    m_actualRoutingStrategy = "/localhost/nfd/strategy/SAF";
  } else if (routingStrategy == "NCC")
  {
    fprintf(stderr, "Installing NCC Strategy...\n");
    m_actualRoutingStrategy = "/localhost/nfd/strategy/ncc";
  } else
  {
    fprintf(stderr, "Error installing strategy - invalid fwStrategy selected...\n");
    return 1;
  }

  // ndn::StrategyChoiceHelper::InstallAll("/prefix", "/localhost/nfd/strategy/broadcast");


  // Installing global routing interface on all nodes
  ndn::GlobalRoutingHelper ndnGlobalRoutingHelper;
  ndnGlobalRoutingHelper.InstallAll();


  // Installing multimedia consumer
  ns3::ndn::AppHelper consumerHelper("ns3::ndn::FileConsumerCbr::MultimediaConsumer");
  consumerHelper.SetAttribute("AllowUpscale", BooleanValue(true));
  consumerHelper.SetAttribute("AllowDownscale", BooleanValue(false));
  consumerHelper.SetAttribute("ScreenWidth", UintegerValue(1920));
  consumerHelper.SetAttribute("ScreenHeight", UintegerValue(1080));
  consumerHelper.SetAttribute("StartRepresentationId", StringValue("auto"));
  consumerHelper.SetAttribute("MaxBufferedSeconds", UintegerValue(60));
  consumerHelper.SetAttribute("StartUpDelay", StringValue("0.1"));
  consumerHelper.SetAttribute("AdaptationLogic", StringValue(dashAdaptationLogic));


  std::cout << "DASH Player using " << dashAdaptationLogic << std::endl;

  // Randomize Client File Selection
  UniformVariable randomStartTime(0,60);
  for(uint32_t i=0; i<client.size (); i++)
  {
    // TODO: Make some logic to decide which file to request
    unsigned int randomNumber =  randInt.GetInteger(0,numServers-1);
    std::string mpdFile = "/myprefix" + boost::lexical_cast<std::string>(randomNumber) + "/BBB-2s-" + boost::lexical_cast<std::string>(randomNumber) + ".mpd";
    int startTime = randomStartTime.GetInteger(0,60);

    consumerHelper.SetAttribute("MpdFileToRequest", StringValue(std::string(mpdFile)));
    ApplicationContainer consumer = consumerHelper.Install (client[i]);

    std::cout << "Client " << i << " is Node " << client[i]->GetId() << " and requests " << mpdFile << " after " << startTime << " seconds" << std::endl;

    // Start and stop the consumer
    consumer.Start (Seconds(startTime)); // TODO: Start at randomized time
    consumer.Stop (Seconds(1500.0));
  }


  Config::ConnectWithoutContext("/NodeList/*/ApplicationList/*/FileDownloadFinished",
                               MakeCallback(&FileDownloadedTrace));


   // Producer
  ndn::AppHelper producerHelper("ns3::ndn::FileServer");


  for (uint32_t i = 0; i < server.size(); i++)
  {
    std::string serverPrefix = "/myprefix" + boost::lexical_cast<std::string>(i);
    ndn::StrategyChoiceHelper::InstallAll(serverPrefix, m_actualRoutingStrategy);


    //std::cout << "Server prefix: " << serverPrefix << std::endl;

    // Producer will reply to all requests starting with /myprefix
    producerHelper.SetPrefix(serverPrefix);
    producerHelper.SetAttribute("ContentDirectory", StringValue("/home/ckreuz/multimediaData/"));
    producerHelper.Install(server[i]); // install to servers

    // check if we should also use fake file server
    if (serverType == "fake")
    {
      ndn::AppHelper producerHelper("ns3::ndn::FakeFileServer");
 
      // Producer will reply to all requests starting with /prefix
      producerHelper.SetPrefix(serverPrefix + "/AVC/BBB");
      producerHelper.SetAttribute("MetaDataFile", StringValue("/home/ckreuz/multimediaData/AVC/BBB/files.csv"));
      producerHelper.Install(server[i]); // install to some node from nodelist
    }


    ndnGlobalRoutingHelper.AddOrigins(serverPrefix, server[i]);
  }



  // Calculate and install FIBs
  ndn::GlobalRoutingHelper::CalculateAllPossibleRoutes();
  // ndn::GlobalRoutingHelper::CalculateRoutes();






  Simulator::Stop(Seconds(1600.0));
  
  
  boost::filesystem::path dir(outputFolder);
  if(boost::filesystem::create_directory(dir))
  {
    std::cerr<< "Directory Created: "<< outputFolder << std::endl;
  }

  ndn::DASHPlayerTracer::InstallAll(outputFolder + "/dash-output.txt");



  std::cout << "Starting simulation..." << std::endl;

  Simulator::Run();
  Simulator::Destroy();

  std::cout << "Simulation ended" << std::endl;

  return 0;
}

} // namespace ns3

int
main(int argc, char* argv[])
{
  return ns3::main(argc, argv);
}




