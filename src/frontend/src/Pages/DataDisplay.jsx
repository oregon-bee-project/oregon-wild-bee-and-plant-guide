import { Box, Flex, Skeleton, Button } from "@chakra-ui/react";
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
        {locationData && locationData.lat == selectedCoords.lat && locationData.long == selectedCoords.lng ? (
          <BeeStatsPanel data={locationData} />
        ) : (
            <Box>
                {Array.from({ length: 9 }).map((_, i) => (
                    <Skeleton key={i} height="30px" width="100%" mb="18px" />
                ))}
            </Box>
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
