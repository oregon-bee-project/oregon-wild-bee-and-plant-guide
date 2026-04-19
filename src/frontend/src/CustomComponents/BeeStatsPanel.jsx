import {
  Badge,
  Box,
  Flex,
  Text,
  Image,
  SimpleGrid,
  VStack,
  Heading,
} from "@chakra-ui/react";
import { LuInfo } from "react-icons/lu";
import ImageLightbox from "./ImageLightbox";
import DataContextInfo from "./DataContextInfo";

const BeeStatsPanel = ({ data }) => {
  if (!data || !data.response) return null;

  const { response, region_type, region_name, region_key, lat, long} = data;
  const {
    numRows,
    numUniqueBees,
    numUniquePlants,
    mostCommonBees,
    mostCommonPlant,
  } = response;

  return (
    <Box bg="white" p={{ base: 4, md: 6 }} borderRadius="2xl" boxShadow="lg" width="100%" pos="relative">
      <Box pos="absolute" top={2} left={2}>
        <DataContextInfo title="About This Summary" defaultOpen>
          <Text>This summary shows the most commonly observed bees and plants in your selected area. The data comes from real observations recorded by bee researchers and community scientists across Oregon.</Text>
          <Text>An <strong>observation</strong> is a single recorded instance of a bee being found on a specific plant. The "obs." numbers you see throughout this page represent how many times that bee or plant was recorded — a higher number means it was spotted more frequently.</Text>
          <Text><strong>Most Common Bees</strong> lists the top 5 bee species seen most often in this area. Bees are listed by their scientific names (for example, <em>Osmia</em> is a genus of mason bees).</Text>
          <Text><strong>Most Common Plant</strong> highlights which flowering plant was visited by bees more than any other in this area, along with which bee species visit it most.</Text>
          <Text fontSize="sm" fontStyle="italic" color="orange.700" bg="orange.50" px={3} py={2} borderRadius="md">Keep in mind that data has been recorded since 2017 and some areas have more observations than others, so a region with fewer total records may not fully represent all the bees and plants that live there.</Text>
        </DataContextInfo>
      </Box>
      <VStack spacing={{ base: 4, md: 6 }} align="stretch">
        <Heading size="lg" textAlign="center">
          {region_name}
        </Heading>

        <Text textAlign="center" fontSize="md" color="gray.600">
          Common Bee & Plant Summary
        </Text>

        {/* Top Stats */}
        <SimpleGrid columns={{ base: 1, md: 3 }} spacing={4}>
          <Box p={{ base: 3, md: 4 }} borderRadius="xl" boxShadow="sm" bg="gray.50">
            <Text fontWeight="bold" fontSize="sm">
              Total Records
            </Text>
            <Text fontSize="2xl">{numRows.toLocaleString()}</Text>
          </Box>

          <Box p={{ base: 3, md: 4 }} borderRadius="xl" boxShadow="sm" bg="gray.50">
            <Text fontWeight="bold" fontSize="sm">
              Unique Bee Species
            </Text>
            <Text fontSize="2xl">{numUniqueBees}</Text>
          </Box>

          <Box p={{ base: 3, md: 4 }} borderRadius="xl" boxShadow="sm" bg="gray.50">
            <Text fontWeight="bold" fontSize="sm">
              Unique Plant Species
            </Text>
            <Text fontSize="2xl">{numUniquePlants}</Text>
          </Box>
        </SimpleGrid>

        {/* Feature Section */}
        <Flex direction={{ base: "column", md: "row" }} gap={{ base: 4, md: 6 }}>
          {/* Most Common Bee */}
          <Box flex={1} p={{ base: 4, md: 5 }} borderRadius="2xl" boxShadow="md" bg="yellow.50">
            <Heading size="sm" mb={2}>
              🐝 Most Common Bees
            </Heading>
            <VStack align="stretch" spacing={2}>
              {mostCommonBees?.map((bee, idx) => (
                <Flex key={idx} justify="space-between" align="center">
                  <Text fontStyle="italic" fontWeight="bold">{bee.scientificName}</Text>
                  <Badge colorScheme="purple">{bee.count} obs.</Badge>
                </Flex>
              ))}
            </VStack>
          </Box>

          {/* Most Common Plant */}
          <Box flex={1} p={{ base: 4, md: 5 }} borderRadius="2xl" boxShadow="md" bg="green.50">
            <Heading size="sm" mb={2}>
              🌿 Most Common Plant
            </Heading>
            {(() => {
              const displayName = mostCommonPlant.commonName || mostCommonPlant.iNatTaxonName || "N/A";
              const isScientific = !mostCommonPlant.commonName || mostCommonPlant.commonName === mostCommonPlant.iNatTaxonName;
              const showSci = mostCommonPlant.iNatTaxonName && mostCommonPlant.commonName && mostCommonPlant.commonName !== mostCommonPlant.iNatTaxonName;
              return (
                <Flex align="baseline" gap={2} wrap="wrap">
                  <Text fontSize="lg" fontWeight="bold" fontStyle={isScientific ? "italic" : "normal"}>
                    {displayName}
                  </Text>
                  {showSci && (
                    <Text fontStyle="italic" color="gray.600" fontSize="md">
                      {mostCommonPlant.iNatTaxonName}
                    </Text>
                  )}
                </Flex>
              );
            })()}
            <Text mt={2}>Observed Interactions: {mostCommonPlant.count}</Text>

            {mostCommonPlant.topBees?.length > 0 && (
              <Box mt={3}>
                <Text fontWeight="bold" fontSize="sm" mb={1}>Top Bee Visitors:</Text>
                <VStack align="stretch" spacing={1}>
                  {mostCommonPlant.topBees.map((bee, idx) => (
                    <Flex key={idx} justify="space-between" align="center" fontSize="sm">
                      <Text fontStyle="italic">{bee.scientificName}</Text>
                      <Badge colorScheme="purple">{bee.count} obs. with this plant</Badge>
                    </Flex>
                  ))}
                </VStack>
              </Box>
            )}

            {mostCommonPlant.iNatURL && (
              <ImageLightbox src={mostCommonPlant.iNatURL} alt={mostCommonPlant.commonName || mostCommonPlant.iNatTaxonName}>
                <Image
                  src={mostCommonPlant.iNatURL}
                  alt={mostCommonPlant.commonName || mostCommonPlant.iNatTaxonName}
                  borderRadius="xl"
                  mt={4}
                  maxH="200px"
                  objectFit="cover"
                />
              </ImageLightbox>
            )}
          </Box>
        </Flex>

        <Flex align="center" justify="center" gap={2} color="gray.500" fontSize="xs" mt={2}>
          <LuInfo />
          <Text>
            Region Type: {region_type} | Lat: {lat} | Long: {long}
          </Text>
        </Flex>
      </VStack>
    </Box>
  );
};

export default BeeStatsPanel;
