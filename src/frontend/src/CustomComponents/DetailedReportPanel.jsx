import {
  Box,
  Flex,
  Text,
  Image,
  SimpleGrid,
  VStack,
  HStack,
  Heading,
  Badge,
} from "@chakra-ui/react";
import { LuInfo } from "react-icons/lu";
import ImageLightbox from "./ImageLightbox";

const SEASON_COLORS = {
  Spring: "green",
  Summer: "yellow",
  Fall:   "orange",
  Winter: "blue",
};

const SeasonBar = ({ springCount, summerCount, fallCount, winterCount }) => {
  const seasons = [
    { label: "Spr", count: springCount, color: "green.400" },
    { label: "Sum", count: summerCount, color: "yellow.400" },
    { label: "Fall", count: fallCount,  color: "orange.400" },
    { label: "Win", count: winterCount, color: "blue.300" },
  ];
  const total = seasons.reduce((acc, s) => acc + s.count, 0);
  if (total === 0) return null;

  return (
    <Flex gap={1} align="center" mt={1}>
      {seasons.map(({ label, count, color }) => {
        const pct = Math.round((count / total) * 100);
        if (pct === 0) return null;
        return (
          <Flex
            key={label}
            bg={color}
            borderRadius="sm"
            px={1}
            align="center"
            justify="center"
            style={{ width: `${pct}%`, minWidth: "28px" }}
          >
            <Text fontSize="2xs" fontWeight="bold" color="gray.800">
              {label}
            </Text>
          </Flex>
        );
      })}
    </Flex>
  );
};

const BeeCard = ({ bee }) => {
  const {
    scientificName,
    count,
    maleCount,
    femaleCount,
    springCount,
    summerCount,
    fallCount,
    winterCount,
    topPlants,
  } = bee;

  return (
    <Box
      borderWidth="1px"
      borderRadius="xl"
      p={4}
      bg="white"
      boxShadow="sm"
    >
      <Flex justify="space-between" align="flex-start" wrap="wrap" gap={2}>
        <Box flex="1">
          <Text fontWeight="bold" fontStyle="italic" fontSize="md">
            {scientificName}
          </Text>
          <HStack spacing={3} mt={1} flexWrap="wrap">
            <Badge colorScheme="purple">{count} obs.</Badge>
            {maleCount > 0 && <Badge colorScheme="blue">♂ {maleCount}</Badge>}
            {femaleCount > 0 && <Badge colorScheme="pink">♀ {femaleCount}</Badge>}
          </HStack>
          <Box mt={2}>
            <Text fontSize="xs" color="gray.500" mb={1}>Seasonal activity</Text>
            <SeasonBar
              springCount={springCount}
              summerCount={summerCount}
              fallCount={fallCount}
              winterCount={winterCount}
            />
          </Box>
        </Box>
      </Flex>

      {topPlants?.length > 0 && (
        <Box mt={3}>
          <Text fontSize="xs" fontWeight="bold" color="gray.600" mb={2}>
            Top Plants Visited
          </Text>
          <VStack align="stretch" spacing={2}>
            {topPlants.map((plant, idx) => (
              <Flex key={idx} align="center" gap={2}>
                {plant.image && (
                  <ImageLightbox src={plant.image} alt={plant.commonName || plant.scientificName}>
                    <Image
                      src={plant.image}
                      alt={plant.commonName || plant.scientificName}
                      boxSize="36px"
                      objectFit="cover"
                      borderRadius="md"
                      flexShrink={0}
                    />
                  </ImageLightbox>
                )}
                <Flex flex="1" minW={0} align="baseline" gap={2} wrap="wrap">
                  {(() => {
                    const displayName = plant.commonName || plant.scientificName || `Plant #${plant.plantINatId}`;
                    const isScientific = !plant.commonName || plant.commonName === plant.scientificName;
                    return (
                      <Text fontSize="md" fontWeight="semibold" fontStyle={isScientific ? "italic" : "normal"} noOfLines={1}>
                        {displayName}
                      </Text>
                    );
                  })()}
                  {plant.scientificName && plant.commonName && plant.commonName !== plant.scientificName && (
                    <Text fontSize="sm" fontStyle="italic" color="gray.500" noOfLines={1}>
                      {plant.scientificName}
                    </Text>
                  )}
                </Flex>
                <Badge colorScheme="green" flexShrink={0}>{plant.count}</Badge>
              </Flex>
            ))}
          </VStack>
        </Box>
      )}
    </Box>
  );
};

const DetailedReportPanel = ({ data }) => {
  if (!data || !data.response) return null;

  const { response, region_type, region_name, lat, long } = data;
  const {
    numRows,
    numUniqueBees,
    numUniquePlants,
    totalMales,
    totalFemales,
    beeList,
  } = response;

  return (
    <Box p={{ base: 4, md: 6 }} width="100%">
      <VStack spacing={{ base: 4, md: 6 }} align="stretch">
        {/* Header */}
        <Heading size="lg" textAlign="center">
          {region_name}
        </Heading>
        <Text textAlign="center" fontSize="md" color="gray.600">
          Detailed Bee & Plant Species Report
        </Text>

        {/* Summary stats */}
        <SimpleGrid columns={{ base: 2, md: 5 }} spacing={3}>
          {[
            { label: "Total Records",       value: numRows?.toLocaleString() },
            { label: "Bee Species",          value: numUniqueBees },
            { label: "Plant Species",        value: numUniquePlants },
            { label: "Males Observed",       value: totalMales },
            { label: "Females Observed",     value: totalFemales },
          ].map(({ label, value }) => (
            <Box key={label} p={3} borderRadius="xl" boxShadow="sm" bg="gray.50">
              <Text fontWeight="bold" fontSize="xs" color="gray.500">{label}</Text>
              <Text fontSize="xl" fontWeight="semibold">{value ?? "—"}</Text>
            </Box>
          ))}
        </SimpleGrid>

        {/* Bee species list */}
        <Box>
          <Heading size="sm" mb={3}>
            All Bee Species ({beeList?.length ?? 0})
          </Heading>
          <VStack align="stretch" spacing={3}>
            {beeList?.map((bee, idx) => (
              <BeeCard key={idx} bee={bee} />
            ))}
          </VStack>
        </Box>

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

export default DetailedReportPanel;
