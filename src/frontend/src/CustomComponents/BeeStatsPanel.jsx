import {
  Box,
  Flex,
  Text,
  Image,
  SimpleGrid,
  VStack,
  Heading,
} from "@chakra-ui/react";

const BeeStatsPanel = ({ data }) => {
  if (!data || !data.response) return null;

  const { response, county } = data;
  const {
    numRows,
    numUniqueBees,
    numUniquePlants,
    mostCommonBee,
    mostCommonPlant,
  } = response;

  return (
    <Box bg="white" p={6} borderRadius="2xl" boxShadow="lg" width="100%">
      <VStack spacing={6} align="stretch">
        {/* County Header */}
        <Heading size="lg" textAlign="center">
          {county} County
        </Heading>

        <Text textAlign="center" fontSize="md" color="gray.600">
          Common Bee & Plant Summary
        </Text>

        {/* Top Stats */}
        <SimpleGrid columns={{ base: 1, md: 3 }} spacing={4}>
          <Box p={4} borderRadius="xl" boxShadow="sm" bg="gray.50">
            <Text fontWeight="bold" fontSize="sm">
              Total Records
            </Text>
            <Text fontSize="2xl">{numRows.toLocaleString()}</Text>
          </Box>

          <Box p={4} borderRadius="xl" boxShadow="sm" bg="gray.50">
            <Text fontWeight="bold" fontSize="sm">
              Unique Bee Species
            </Text>
            <Text fontSize="2xl">{numUniqueBees}</Text>
          </Box>

          <Box p={4} borderRadius="xl" boxShadow="sm" bg="gray.50">
            <Text fontWeight="bold" fontSize="sm">
              Unique Plant Species
            </Text>
            <Text fontSize="2xl">{numUniquePlants}</Text>
          </Box>
        </SimpleGrid>

        {/* Feature Section */}
        <Flex direction={{ base: "column", md: "row" }} gap={6}>
          {/* Most Common Bee */}
          <Box flex={1} p={5} borderRadius="2xl" boxShadow="md" bg="yellow.50">
            <Heading size="sm" mb={2}>
              🐝 Most Common Bee
            </Heading>
            <Text fontSize="lg" fontWeight="bold" fontStyle="italic">
              {mostCommonBee.scientificName || "N/A"}
            </Text>
            <Text mt={2}>Observations: {mostCommonBee.count}</Text>
          </Box>

          {/* Most Common Plant */}
          <Box flex={1} p={5} borderRadius="2xl" boxShadow="md" bg="green.50">
            <Heading size="sm" mb={2}>
              🌿 Most Common Plant
            </Heading>
            <Text fontSize="lg" fontWeight="bold">
              {mostCommonPlant.commonName ||
                mostCommonPlant.iNatTaxonName ||
                "N/A"}
            </Text>
            {mostCommonPlant.iNatTaxonName && (
              <Text fontStyle="italic" color="gray.600">
                {mostCommonPlant.iNatTaxonName}
              </Text>
            )}
            <Text mt={2}>Observations: {mostCommonPlant.count}</Text>
            {mostCommonPlant.iNatURL && (
              <Image
                src={mostCommonPlant.iNatURL}
                alt={
                  mostCommonPlant.commonName || mostCommonPlant.iNatTaxonName
                }
                borderRadius="xl"
                mt={4}
                maxH="200px"
                objectFit="cover"
              />
            )}
          </Box>
        </Flex>
      </VStack>
    </Box>
  );
};

export default BeeStatsPanel;
