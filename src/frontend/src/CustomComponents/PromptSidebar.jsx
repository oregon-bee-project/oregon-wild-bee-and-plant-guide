import { Box, Button, Text, VStack, Flex } from "@chakra-ui/react";
import PromptItem from "./PromptItem";
import { useState } from "react";

// Defined custom prompts
const prompts = [
  {
    id: 1,
    title: "Common Bees",
    description: "What is the most common plant and bee in my area?",
  },
  {
    id: 2,
    title: "Plants",
    description: "What plants should I grow to support bees in my area?",
  },
  {
    id: 3,
    title: "Detailed Summary Report",
    description: "Show me a detailed report of bee and plant species in my area"
  }
];

const PromptSidebar = ({
    display,
    activePrompt,
    setActivePrompt,
    fetchLocationData,
    onPromptSelect
}) => {
  return (
    <Box
      w={{ base: "100%", md: "300px" }}
      h={{ base: "auto", md: "100%" }}
      borderRadius="md"
      borderWidth="2px"
      p={4}
      display={display}
      flexDirection="column"
      justifyContent="space-between"
    >
      {/* vertical stack of labels, input fields, buttons, etc. */}
      <VStack align="stretch" spacing={4}>
        <Text>Prompts</Text>
        {prompts.map((prompt) => (
          <PromptItem
            key={prompt.id}
            title={prompt.title}
            description={prompt.description}
            selected={activePrompt === prompt.id}
            onClick={() => setActivePrompt(prompt.id)}
          />
        ))}
      </VStack>
      <Flex justify="center">
        <Button
          colorScheme="blue"
          isDisabled={!activePrompt}
          onClick={() => {
            const selected = prompts.find((p) => p.id === activePrompt);
            console.log("Selected prompt:", selected);
            fetchLocationData();
            onPromptSelect?.(); // Close drawer on mobile after running prompt
          }}
        >
          Run Selected Prompt
        </Button>
      </Flex>
    </Box>
  );
};

export default PromptSidebar;
