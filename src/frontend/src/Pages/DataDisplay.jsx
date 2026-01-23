import { Box, Flex, Button, Heading, Text, Stack } from "@chakra-ui/react";
import { LuFileUp } from "react-icons/lu";
import BeeStatsPanel from "../CustomComponents/BeeStatsPanel";

const DataDisplay = ({ locationData, selectedCoords }) => {
  // On click of export, send post request to backend to generate CSV
  // Render API base
  const API_BASE = import.meta.env.PROD
    ? "https://bee-data-api.onrender.com" // this is what the url prefix will be in production
    : "";
  const handleExport = async () => {
    if (!locationData) return;

    try {
      const response = await fetch(`${API_BASE}/api/export-csv`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          selectedCoords,
        }),
      });

      if (!response.ok) {
        throw new Error("Failed to export CSV");
      }

      const blob = await response.blob();
      const url = window.URL.createObjectURL(blob);

      const link = document.createElement("a");
      link.href = url;
      link.download = "export.csv"; // filename
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
        {locationData && <BeeStatsPanel data={locationData} />}
      </Box>
      <Flex gap="8px">
        <Button
          flex="1"
          bg="blue.600"
          _hover={{ bg: "blue.500" }}
          onClick={handleExport}
        >
          <LuFileUp /> Export Results
        </Button>
      </Flex>
    </Flex>
  );
};

export default DataDisplay;
