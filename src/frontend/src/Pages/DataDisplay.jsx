import { Box, Flex, Text, Button } from "@chakra-ui/react";
import { LuFileUp } from "react-icons/lu";
import BeeStatsPanel from "../CustomComponents/BeeStatsPanel";

const DataDisplay = ({ locationData }) => {
  return (
    <Flex direction="column" flex="1" align="stretch" gap={2}>
      {/* data display area */}
      <Box
        flex="1"
        borderWidth="2px"
        borderRadius="md"
        bg="gray.100"
        alignItems="center"
        justifyContent="center"
        p={2}
        overflowY="auto"
      >
        {locationData ? (
          //<pre>{JSON.stringify(locationData, null, 2)}</pre>
          <BeeStatsPanel data={locationData} />
        ) : (
          <Text>
            No location data found. Pick a valid location in Oregon and click
            "Set Location".
          </Text>
        )}
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
