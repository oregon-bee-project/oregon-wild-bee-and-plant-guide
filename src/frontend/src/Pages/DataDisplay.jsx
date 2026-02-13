import { Box, Flex, Button, Heading, Text, VStack, List, ListItem } from "@chakra-ui/react";
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
      link.download = "export.pdf"; // filename
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
            <VStack align="stretch" spacing={4}>
              <Heading size="lg" textAlign="center">
                Best plants to support bees in your area
              </Heading>
              <Box>
                <Text fontWeight="bold" mb={2}>
                  Top 5 plants:
                </Text>
                {Array.isArray(locationData.response) && locationData.response.length > 0 ? (
                  <List.Root as="ol" listStyleType="decimal" pl={4} spacing={1}>
                    {locationData.response.map((plant, idx) => (
                      <List.Item key={idx} fontStyle="italic">
                        {plant}
                      </List.Item>
                    ))}
                  </List.Root>
                ) : (
                  <Text color="gray.600" fontStyle="italic">
                    No plants found. Please try selecting a different location.
                  </Text>
                )}
              </Box>
              <Box>
                <Text fontWeight="bold" mb={2}>
                  JSON response:
                </Text>
                <Box
                  as="pre"
                  p={4}
                  bg="gray.50"
                  borderRadius="md"
                  fontSize="sm"
                  fontFamily="mono"
                  overflowX="auto"
                  whiteSpace="pre-wrap"
                >
                  {JSON.stringify(locationData, null, 2)}
                </Box>
              </Box>
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
