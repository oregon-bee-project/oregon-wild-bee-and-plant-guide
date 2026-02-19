import { Box, Flex, Button, Heading, Text, Stack } from "@chakra-ui/react";
import { LuFileUp, LuRefreshCcw } from "react-icons/lu";
import BeeStatsPanel from "../CustomComponents/BeeStatsPanel";

const DataDisplay = ({
  locationData,
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
