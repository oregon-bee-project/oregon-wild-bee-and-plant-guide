import { Box, Flex, Button, Heading, Text, VStack, SimpleGrid, Image } from "@chakra-ui/react";
import { LuFileUp, LuRefreshCcw } from "react-icons/lu";
import BeeStatsPanel from "../CustomComponents/BeeStatsPanel";

const DataDisplay = ({
  locationData,
  activePrompt,
  selectedCoords,
  selectedRegion,
  setActivePage,
  setActivePrompt,
  setSelectedCoords,
}) => {
  // On click of export, send post request to backend to generate CSV
  // Render API base
  const API_BASE = import.meta.env.PROD
    ? "https://bee-data-api.onrender.com" // this is what the url prefix will be in production
    : "";
  const handleExport = async () => {
    if (!locationData) return;

    try {
      const response = await fetch(`${API_BASE}/api/export-pdf`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          selectedCoords,
          region_type: selectedRegion,
        }),
      });
      console.log(selectedRegion);

      if (!response.ok) {
        throw new Error("Failed to export PDF");
      }

      const blob = await response.blob();
      const url = window.URL.createObjectURL(blob);

      const link = document.createElement("a");
      link.href = url;
      //look for file name
      const disposition = response.headers.get("Content-Disposition");
      let filename = "export.pdf"; // fallback

      if (disposition && disposition.includes("filename=")) {
        filename = disposition.split("filename=")[1].replace(/"/g, ""); // remove quotes if present
      }

      link.download = filename; // filename
      link.click();

      window.URL.revokeObjectURL(url);
    } catch (error) {
      console.error("Export error:", error);
    }
  };

  // Determine which branch to render
  const shouldRenderPlants = locationData && activePrompt === 2;

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
        {shouldRenderPlants ? (
          <Box bg="white" p={{ base: 4, md: 6 }} borderRadius="2xl" boxShadow="lg" width="100%">
            <VStack spacing={{ base: 4, md: 6 }} align="stretch">
              <Heading size="lg" textAlign="center">
                {locationData.region_name || "Best plants to support bees in your area"}
              </Heading>
              <Text textAlign="center" fontSize="md" color="gray.600">
                Top 5 plants to support bees in your area
              </Text>
              {Array.isArray(locationData.response) && locationData.response.length > 0 ? (
                <SimpleGrid columns={{ base: 1, md: 2 }} spacing={4}>
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
                      >
                        <Heading size="sm" mb={2}>
                          #{rank}
                        </Heading>
                        <Text fontSize="lg" fontWeight="bold">
                          {commonName}
                        </Text>
                        {iNatTaxonName ? (
                          <Text fontStyle="italic" color="gray.600">
                            {iNatTaxonName}
                          </Text>
                        ) : null}
                        {iNatURL ? (
                          <Image
                            src={iNatURL}
                            alt={commonName}
                            borderRadius="xl"
                            mt={4}
                            maxH="200px"
                            objectFit="cover"
                          />
                        ) : null}
                      </Box>
                    );
                  })}
                </SimpleGrid>
              ) : (
                <Text color="gray.600" fontStyle="italic">
                  No plants found. Please try selecting a different location.
                </Text>
              )}
            </VStack>
          </Box>
        ) : (
          <BeeStatsPanel data={locationData} />
        )}
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
          }}
        >
          <LuRefreshCcw /> Try a New Prompt
        </Button>
        {activePrompt === 1 && (
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
