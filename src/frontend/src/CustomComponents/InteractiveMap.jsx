import { Box, Flex, VStack, Text, Button } from "@chakra-ui/react";
import { LuMapPin } from "react-icons/lu";

const InteractiveMap = () => {
  return (
    <Flex flex="1" direction="column">
      <VStack
        align="stretch"
        flex="1"       
        spacing={4}    
      >
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

        <Button>
          <LuMapPin /> Set Location
        </Button>
      </VStack>
    </Flex>
  );
};

export default InteractiveMap;