import { Box, Flex, Button } from "@chakra-ui/react";
import { LuFileUp } from "react-icons/lu";
import BeeStatsPanel from "../CustomComponents/BeeStatsPanel";

const DataDisplay = ({ locationData, selectedCoords }) => {
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
        <Button flex="1" bg="blue.600" _hover={{ bg: "blue.500" }}>
          <LuFileUp /> Export Results
        </Button>
      </Flex>
    </Flex>
  );
};

export default DataDisplay;
