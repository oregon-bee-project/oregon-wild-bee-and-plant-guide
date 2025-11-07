import { Box, Flex, Text, Button } from "@chakra-ui/react";
import { LuArrowLeftRight, LuFileUp } from "react-icons/lu";

const DataDisplay = () => {
  return (
    <Flex direction="column" flex="1" align="stretch" gap={2}>

      {/* map area */}
      <Box
        flex="1"
        borderWidth="2px"
        borderRadius="md"
        bg="gray.100"
        display="flex"
        alignItems="center"
        justifyContent="center"
      >
        <Text>Data/Results Displayed Here</Text>
      </Box>
      <Flex gap="8px">
        <Button flex="1" bg="green.400">
          <LuArrowLeftRight /> Change Location
        </Button>
        <Button flex="1" bg="blue.400">
          <LuFileUp /> Export Results
        </Button>
      </Flex>
    </Flex>
  );
};

export default DataDisplay;