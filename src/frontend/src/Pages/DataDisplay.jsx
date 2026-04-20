import { Box, Flex, Button, Heading, Text, VStack, SimpleGrid, Image } from "@chakra-ui/react";
import { LuFileUp, LuRefreshCcw } from "react-icons/lu";
import BeeStatsPanel from "../CustomComponents/BeeStatsPanel";
import DetailedReportPanel from "../CustomComponents/DetailedReportPanel";

const DataDisplay = ({
  locationData,
  activePrompt,
  selectedCoords,
  selectedRegion,
  setActivePage,
  setActivePrompt,
  setSelectedCoords,
  setMapResetTrigger,
}) => {
  // On click of export, send post request to backend to generate PDF
  // Render API base
  const API_BASE = import.meta.env.PROD
    ? "https://bee-data-api.onrender.com" // this is what the url prefix will be in production
    : "";

  const exportEndpointMap = {
    1: "/api/export-pdf/",
    3: "/api/export-detailed-pdf/",
  };

  const handleExport = async () => {
    if (!locationData) return;

    const exportEndpoint = exportEndpointMap[activePrompt] ?? "/api/export-pdf/";

    try {
      const response = await fetch(`${API_BASE}${exportEndpoint}`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          selectedCoords,
          region_type: selectedRegion,
        }),
      });

      if (!response.ok) {
        throw new Error("Failed to export PDF");
      }

      const blob = await response.blob();
      const url = window.URL.createObjectURL(blob);

      const link = document.createElement("a");
      link.href = url;
      const disposition = response.headers.get("Content-Disposition");
      let filename = "export.pdf"; // fallback

      if (disposition && disposition.includes("filename=")) {
        filename = disposition.split("filename=")[1].replace(/"/g, ""); // remove quotes if present
      }

      link.download = filename;
      link.click();

      window.URL.revokeObjectURL(url);
    } catch (error) {
      console.error("Export error:", error);
    }
  };

  return (
    <Flex direction="column" flex="1" align="stretch" gap={2}>
      {/* data display area */}
      <Box
        flex="1"
        borderWidth="2px"
        borderRadius="md"
        alignItems="center"
        justifyContent="center"
        p={2}
        overflowY="auto"
      >
        {locationData && activePrompt === 1 && <BeeStatsPanel data={locationData} />}
        {locationData && activePrompt === 2 && (() => {
          const plants = locationData.response;
          const hasPlants = Array.isArray(plants) && plants.length > 0;
          const totalScore = hasPlants
            ? plants.reduce((sum, p) => sum + (Number(p?.score) || 0), 0)
            : 0;
          return (
            <Box bg="white" p={{ base: 3, md: 5 }} borderRadius="xl" boxShadow="md" width="100%" maxW="100%">
              <VStack spacing={4} align="stretch">
                <Heading size="md" textAlign="center">
                  {locationData.region_name || "Best plants to support bees in your area"}
                </Heading>
                <Text textAlign="center" fontSize="sm" color="gray.600">
                  Top 5 plants to support bees in your area
                </Text>
                {hasPlants ? (
                  <VStack align="stretch" spacing={4} width="100%">
                    {plants.map((plant, idx) => {
                      const commonName = plant?.commonName ?? (typeof plant === "string" ? `Plant #${plant}` : "Unknown");
                      const iNatTaxonName = plant?.iNatTaxonName ?? "";
                      const iNatURL = plant?.iNatURL ?? "";
                      const topBees = Array.isArray(plant?.topBees) ? plant.topBees : [];
                      const score = Number(plant?.score);
                      const sharePct = totalScore > 0 && !Number.isNaN(score) ? (score / totalScore) * 100 : null;
                      return (
                        <Box
                          key={idx}
                          borderRadius="lg"
                          bg="green.50"
                          borderWidth="1px"
                          borderColor="green.100"
                          overflow="hidden"
                          pb={4}
                        >
                          <Text fontSize="md" fontWeight="bold" px={3} pt={3} noOfLines={2}>
                            {commonName}
                          </Text>
                          {iNatTaxonName ? (
                            <Text fontStyle="italic" color="gray.600" fontSize="sm" px={3} pb={2} noOfLines={1}>
                              {iNatTaxonName}
                            </Text>
                          ) : null}
                          <Flex
                            direction={{ base: "column", md: "row" }}
                            align={{ base: "stretch", md: "flex-start" }}
                            minH={{ base: "auto", md: "220px" }}
                          >
                            {iNatURL ? (
                              <Box flex={1} h={{ base: "200px", md: "220px" }} flexShrink={0} bg="green.50" overflow="hidden">
                                <Image
                                  src={iNatURL}
                                  alt={commonName}
                                  width="100%"
                                  height="100%"
                                  objectFit="contain"
                                  display="block"
                                />
                              </Box>
                            ) : null}
                            <Box
                              flex={1}
                              p={3}
                              borderLeftWidth={{ md: "1px" }}
                              borderTopWidth={{ base: "1px", md: "0" }}
                              borderColor="green.200"
                            >
                              {sharePct != null && (
                                <Box mb={3} pb={3} borderBottomWidth="1px" borderBottomColor="green.200">
                                  <Text fontSize="xs" color="gray.600" mb={0.5}>
                                    Share of predicted bee–plant interactions (among these 5 plants)
                                  </Text>
                                  <Text fontWeight="bold" fontSize="lg" color="green.700">
                                    {sharePct.toFixed(1)}%
                                  </Text>
                                </Box>
                              )}
                              <Text fontWeight="semibold" fontSize="sm" mb={2} color="gray.700">
                                Top bees this plant supports
                              </Text>
                              {topBees.length > 0 ? (
                                <VStack align="stretch" spacing={1}>
                                  {topBees.map((bee, beeIdx) => (
                                    <Text key={beeIdx} fontStyle="italic" fontSize="sm" noOfLines={1}>
                                      {bee.scientificName ?? "Unknown"}
                                    </Text>
                                  ))}
                                </VStack>
                              ) : (
                                <Text fontSize="sm" color="gray.500" fontStyle="italic">
                                  No bee data for this location
                                </Text>
                              )}
                            </Box>
                          </Flex>
                        </Box>
                      );
                    })}
                  </VStack>
                ) : (
                  <Box
                    p={5}
                    borderRadius="lg"
                    bg="gray.50"
                    borderWidth="1px"
                    borderColor="gray.200"
                    textAlign="center"
                  >
                    <Text color="gray.600" fontStyle="italic" fontSize="sm">
                      No plants found. Please try selecting a different location.
                    </Text>
                  </Box>
                )}
              </VStack>
            </Box>
          );
        })()}
        {locationData && activePrompt === 3 && <DetailedReportPanel data={locationData} />}
      </Box>
      <Flex gap="8px">
        <Button
          flex="1"
          bg="green.600"
          _hover={{ bg: "green.500" }}
          onClick={() => {
            setActivePage("prompts-map");
            setActivePrompt(null);
            setSelectedCoords({ lat: "", lng: "" });
            setMapResetTrigger(prev => prev + 1);
          }}
        >
          <LuRefreshCcw /> Explore again
        </Button>
        {(activePrompt === 1 || activePrompt === 3) && (
          <Button
            flex="1"
            bg="blue.600"
            _hover={{ bg: "blue.500" }}
            onClick={handleExport}
          >
            <LuFileUp /> Export results
          </Button>
        )}
      </Flex>
    </Flex>
  );
};

export default DataDisplay;
