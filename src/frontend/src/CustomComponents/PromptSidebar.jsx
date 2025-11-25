import { Box, Button, Input, Text, VStack, SegmentGroup } from "@chakra-ui/react";

const PromptSidebar = ({ selectedPage, setSelectedPage }) => {
  return (
    <Box
      w="300px"
      h="100%"
      borderRadius="md"
      borderWidth="2px"
      p={4}
      display="flex"
      flexDirection="column"
      justifyContent="space-between"
    >
      {/* vertical stack of labels, input fields, buttons, etc. */}
      <VStack align="stretch" spacing={4}>
        <Text>Prompt Sidebar</Text>
        <Input placeholder="Enter your prompt here" />
        <Button>Submit</Button>
      </VStack>
    </Box>
  );
};

export default PromptSidebar;