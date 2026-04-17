import {
    Box,
    Button,
    Text,
    VStack,
    Portal,
    Select,
    Span,
    Stack,
    createListCollection,
    Flex
} from "@chakra-ui/react";
import PromptItem from "./PromptItem";
import { LuArrowRight } from "react-icons/lu";

const prompts = createListCollection({
  items: [
    {
      label: "Common Bees",
      value: "bees",
      description: "What is the most common plant and bee in my area?",
      id: 1
    },
    {
      label: "Best Plants",
      value: "plants",
      description: "What plants should I grow to support bees in my area?",
      id: 2
    },
    {
      label: "Detailed Summary Report",
      value: "report",
      description: "Show me a detailed report of bee and plant species in my area",
      id: 3
    },
  ],
})

const PromptSidebar = ({
  display,
  activePrompt,
  setActivePrompt,
  fetchLocationData,
  setErrorDialogMsg,
  onPromptSelect,
  showButton = true,
}) => {

  // Convert activePrompt id to select value
  const getSelectedValue = () => {
    const prompt = prompts.items.find(p => p.id === activePrompt)
    return prompt ? [prompt.value] : []
  }

  // Handle select change
  const handleSelectChange = (details) => {
    const selectedValue = details.value[0]
    const selectedPrompt = prompts.items.find(p => p.value === selectedValue)
    if (selectedPrompt) {
      setActivePrompt(selectedPrompt.id)
    }
  }

  return (
    <VStack spacing={0}>
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
        <VStack align="stretch" spacing={4}>
          <Text textStyle="xs">1) What information are you interested in?</Text>
          <Select.Root
            collection={prompts}
            size="sm"
            width="full"
            value={getSelectedValue()}
            onValueChange={handleSelectChange}
          >
            <Select.HiddenSelect />
            <Select.Control>
              <Select.Trigger>
                <Select.ValueText placeholder="Select" />
              </Select.Trigger>
              <Select.IndicatorGroup>
                <Select.Indicator />
              </Select.IndicatorGroup>
            </Select.Control>
            <Portal>
              <Select.Positioner>
                <Select.Content>
                  {prompts.items.map((prompt) => (
                    <Select.Item item={prompt} key={prompt.value}>
                      <Stack gap="0">
                        <Select.ItemText>{prompt.label}</Select.ItemText>
                        <Span color="fg.muted" textStyle="xs">
                          {prompt.description}
                        </Span>
                      </Stack>
                      <Select.ItemIndicator />
                    </Select.Item>
                  ))}
                </Select.Content>
              </Select.Positioner>
            </Portal>
          </Select.Root>
        </VStack>
      </Box>
      {showButton && (
        <Button
          w={{ base: "100%", md: "300px" }}
          bg="green.600"
          _hover={{ bg: "green.500" }}
          isDisabled={!activePrompt}
          onClick={() => {
            fetchLocationData();
            onPromptSelect?.(); // Close drawer on mobile after running prompt
          }}
        >
            Explore the data <LuArrowRight />
        </Button>
      )}
    </VStack>
  );
};

export default PromptSidebar;