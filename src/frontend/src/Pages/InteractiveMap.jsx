import { Box, Flex, Text, Button } from "@chakra-ui/react";
import { LuMapPin } from "react-icons/lu";

const InteractiveMap = () => {
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
        <Text>Map Goes Here</Text>
      </Box>

      {/* button below map */}
      <Button bg="green.400">
        <LuMapPin /> Set Location
      </Button>
    </Flex>
  );
};

export default InteractiveMap;