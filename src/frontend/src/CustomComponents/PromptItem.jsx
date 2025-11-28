import { Box, Text } from "@chakra-ui/react";

const PromptItem = ({ title, description, selected, onClick }) => {
  return (
    <Box
      p={3}
      borderWidth="1px"
      borderRadius="lg"
      cursor="pointer"
      transition="all 0.2s"
      bg={selected ? "blue.300" : "transparent"}
      _hover={{ bg: "gray.200" }}
      onClick={onClick}
    >
      <Text fontWeight="semibold" fontSize="sm">
        {title}
      </Text>
      <Text fontSize="xs" color="gray.600">
        {description}
      </Text>
    </Box>
  );
};

export default PromptItem;
