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
        {locationData && activePrompt === 2 && (
          <Box bg="white" p={{ base: 4, md: 6 }} borderRadius="2xl" boxShadow="lg" width="100%" maxW="100%">
            <VStack spacing={{ base: 5, md: 6 }} align="stretch">
              <Heading size="lg" textAlign="center">
                {locationData.region_name || "Best plants to support bees in your area"}
              </Heading>
              <Text textAlign="center" fontSize="md" color="gray.600">
                Top 5 Plants to Support Bees in Your Area
              </Text>
              {Array.isArray(locationData.response) && locationData.response.length > 0 ? (
                <SimpleGrid columns={{ base: 1, md: 2 }} spacing={{ base: 4, md: 5 }} width="100%">
                  {locationData.response.map((plant, idx) => {
                    const rank = (plant?.rank != null ? plant.rank : idx + 1);
                    const commonName = plant?.commonName ?? (typeof plant === "string" ? `Plant #${plant}` : "Unknown");
                    const iNatTaxonName = plant?.iNatTaxonName ?? "";
                    const iNatURL = plant?.iNatURL ?? "";
                    return (
                      <Box
                        key={idx}
                        p={{ base: 4, md: 5 }}
                        borderRadius="2xl"
                        boxShadow="md"
                        bg="green.50"
                        borderWidth="1px"
                        borderColor="green.100"
                        overflow="hidden"
                      >
                        <Flex align="flex-start" gap={3} mb={2}>
                          <Flex
                            align="center"
                            justify="center"
                            w={8}
                            h={8}
                            borderRadius="full"
                            bg="green.500"
                            color="white"
                            fontWeight="bold"
                            fontSize="sm"
                            flexShrink={0}
                          >
                            {rank}
                          </Flex>
                          <Box flex={1} minW={0}>
                            <Text fontSize="lg" fontWeight="bold" lineHeight="tight">
                              {commonName}
                            </Text>
                            {iNatTaxonName ? (
                              <Text fontStyle="italic" color="gray.600" fontSize="sm" mt={0.5}>
                                {iNatTaxonName}
                              </Text>
                            ) : null}
                          </Box>
                        </Flex>
                        {plant?.score != null && plant?.score !== "" ? (
                          <Box
                            display="inline-block"
                            px={2}
                            py={1}
                            borderRadius="md"
                            bg="white"
                            borderWidth="1px"
                            borderColor="green.200"
                            mb={3}
                          >
                            <Text fontSize="xs" fontWeight="semibold" color="gray.600">
                              Interaction score: {Number(plant.score).toLocaleString(undefined, { maximumFractionDigits: 2 })}
                            </Text>
                          </Box>
                        ) : null}
                        {iNatURL ? (
                          <Box mt={2} mb={3} borderRadius="xl" overflow="hidden" bg="gray.100">
                            <Image
                              src={iNatURL}
                              alt={commonName}
                              width="100%"
                              maxH="200px"
                              objectFit="cover"
                            />
                          </Box>
                        ) : null}
                        {Array.isArray(plant?.topBees) && plant.topBees.length > 0 ? (
                          <Box
                            pt={3}
                            borderTopWidth="1px"
                            borderTopColor="green.200"
                          >
                            <Text fontWeight="bold" fontSize="sm" mb={2} color="gray.700">
                              Top bees this plant supports
                            </Text>
                            <VStack align="stretch" spacing={1.5}>
                              {plant.topBees.map((bee, beeIdx) => (
                                <Flex key={beeIdx} justify="space-between" align="center" fontSize="sm">
                                  <Text fontStyle="italic" noOfLines={1} flex={1} mr={2}>
                                    {bee.scientificName ?? "Unknown"}
                                  </Text>
                                  <Text fontWeight="medium" flexShrink={0}>
                                    {bee.count}
                                  </Text>
                                </Flex>
                              ))}
                            </VStack>
                          </Box>
                        ) : null}
                      </Box>
                    );
                  })}
                </SimpleGrid>
              ) : (
                <Box
                  p={6}
                  borderRadius="xl"
                  bg="gray.50"
                  borderWidth="1px"
                  borderColor="gray.200"
                  textAlign="center"
                >
                  <Text color="gray.600" fontStyle="italic">
                    No plants found. Please try selecting a different location.
                  </Text>
                </Box>
              )}
            </VStack>
          </Box>
        )}
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
            //setSelectedCoords({ lat: "", lng: "" });
          }}
        >
          <LuRefreshCcw /> Try a New Prompt
        </Button>
        {(activePrompt === 1 || activePrompt === 3) && (
          <Button
            flex="1"
            bg="blue.600"
            _hover={{ bg: "blue.500" }}
            onClick={handleExport}
          >
            <LuFileUp /> Export Results
          </Button>
        )}
      </Flex>
    </Flex>
  );
};

export default DataDisplay;
