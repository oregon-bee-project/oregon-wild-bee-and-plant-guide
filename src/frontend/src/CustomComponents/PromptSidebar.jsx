import { useState, useEffect } from "react";
import {
    Box,
    Button,
    Text,
    VStack,
    Portal,
    Select,
    createListCollection,
    RadioCard,
    Icon,
    Input,
    Group
} from "@chakra-ui/react";
import { LuArrowRight, LuFileText, LuTrophy, LuLeaf } from "react-icons/lu";

const prompts = [
    {
      title: "The most common bees",
      value: "bees",
      description: "What are the most common bees and plants in a given location?",
      icon: <LuTrophy />,
      id: 1
    },
    {
      title: "The best plants",
      value: "plants",
      description: "What plants should I grow to support bees in my area?",
      icon: <LuLeaf />,
      id: 2
    },
    {
      title: "A detailed summary report",
      value: "report",
      description: "Show me a detailed report of bee and plant species in my area",
      icon: <LuFileText />,
      id: 3
    },
  ]

const overlays = createListCollection({
  items: [
    { label: "County", value: "county", color: "Orange" },
    { label: "Ecoregion", value: "ecoregion", color: "Green" },
    { label: "National Forest", value: "national-forest", color: "Brown" },
  ],
});

const PromptSidebar = ({
  display,
  activePrompt,
  setActivePrompt,
  fetchLocationData,
  setErrorDialogMsg,
  onPromptSelect,
  showButton = true,
  selectedRegion,
  setSelectedRegion,
  selectedCoords,
  setSelectedCoords,
}) => {

  const [address, setAddress] = useState("");

  // Convert activePrompt id to radio card value
  const getSelectedPromptValue = () => {
    const prompt = prompts.find(p => p.id === activePrompt)
    return prompt ? prompt.value : ""
  }

  // Handle radio card selection
  const handlePromptChange = (details) => {
    const selectedValue = details.value
    const selectedPrompt = prompts.find(p => p.value === selectedValue)
    if (selectedPrompt) {
      setActivePrompt(selectedPrompt.id)
    }
  }

  const handleLayerChange = (details) => {
    const selectedCategory = details.value[0];
    setSelectedRegion(selectedCategory);
  };

  const geocodeAddress = async (address) => {
    const response = await fetch(
      `https://nominatim.openstreetmap.org/search?format=json&q=${encodeURIComponent(address)}`
    );

    const data = await response.json();

    if (data.length > 0) {
      return {
        lat: parseFloat(data[0].lat),
        lng: parseFloat(data[0].lon),
      };
    } else {
      throw new Error("No results found");
    }
  };

  useEffect(() => {
    if (!selectedCoords) return;

    const reverseGeocode = async () => {
      try {
        const response = await fetch(
          `https://nominatim.openstreetmap.org/reverse?format=json&lat=${selectedCoords.lat}&lon=${selectedCoords.lng}`
        );
        const data = await response.json();
        setAddress(data.display_name ?? "");
      } catch {
        // silently fail — map click still works, address just won't populate
      }
    };

    reverseGeocode();
  }, [selectedCoords]);

  const handleSetAddress = async () => {
    if (!address) return;

    try {
      const coords = await geocodeAddress(address);
      setSelectedCoords(coords);
    } catch (err) {
      setErrorDialogMsg("Address not found.");
    }
  };

  return (
    <VStack spacing={0}>
      <Box
        w={{ base: "100%", md: "400px" }}
        h={{ base: "auto", md: "100%" }}
        borderRadius="md"
        borderWidth="2px"
        p={4}
        display={display}
        flexDirection="column"
        justifyContent="space-between"
        overflow="hidden"
      >
        <VStack
          align="stretch"
          spacing={4}
          overflowY="auto"
          flex="1"
          pb={2}    
        >
          <Text>What are you interested in seeing?</Text>
          <RadioCard.Root
            value={getSelectedPromptValue()}
            onValueChange={handlePromptChange}
          >
            <VStack align="stretch">
              {prompts.map((prompt) => (
                <RadioCard.Item key={prompt.value} value={prompt.value}>
                  <RadioCard.ItemHiddenInput />
                  <RadioCard.ItemControl _hover={{ bg: "gray.100", cursor: "pointer" }}>
                    <Icon size="md" color="fg.muted" mb="2px">
                        {prompt.icon}
                    </Icon>
                    <RadioCard.ItemContent>
                      <RadioCard.ItemText>{prompt.title}</RadioCard.ItemText>
                      <RadioCard.ItemDescription>
                        {prompt.description}
                      </RadioCard.ItemDescription>
                    </RadioCard.ItemContent>
                  </RadioCard.ItemControl>
                </RadioCard.Item>
              ))}
            </VStack>
          </RadioCard.Root>

          <Text mt="8px">Summarize data by:</Text>
          <Select.Root
            collection={overlays}
            size="sm"
            width="full"
            value={[selectedRegion || "county"]}
            onValueChange={handleLayerChange}
          >
            <Select.HiddenSelect />
            <Select.Control>
              <Select.Trigger>
                <Select.ValueText placeholder="Select overlay" />
              </Select.Trigger>
              <Select.IndicatorGroup>
                <Select.Indicator />
              </Select.IndicatorGroup>
            </Select.Control>
            <Portal>
              <Select.Positioner>
                <Select.Content>
                  {overlays.items.map((overlay) => (
                    <Select.Item item={overlay} key={overlay.value}>
                      {overlay.label}
                      <Select.ItemIndicator />
                    </Select.Item>
                  ))}
                </Select.Content>
              </Select.Positioner>
            </Portal>
          </Select.Root>

          <Text mt="8px">Choose a location:</Text>
          <Group attached w="full">
          <Input
            flex="1"
            placeholder="Type address or click map"
            value={address}
            onChange={(e) => setAddress(e.target.value)}
            onKeyDown={(e) => {
              if (e.key === 'Enter') {
                handleSetAddress();
              }
            }}
          />
            <Button
              variant="outline"
              bg="bg.subtle"
              textStyle="xs"
              _hover={{ bg: "green.100" }}
              onClick={handleSetAddress}
            >
              Set Location
            </Button>
          </Group>
        </VStack>
      </Box>
      {showButton && (
          <Button
          w={{ base: "100%", md: "100%" }}
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