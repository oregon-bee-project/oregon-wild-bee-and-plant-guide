import { useState, useMemo, useEffect, useRef, useCallback } from "react";
import {
  Box,
  Button,
  Flex,
  Text,
  Image,
  SimpleGrid,
  VStack,
  HStack,
  Heading,
  Badge,
  Spinner,
} from "@chakra-ui/react";
import { LuInfo } from "react-icons/lu";
import ImageLightbox from "./ImageLightbox";
import DataContextInfo from "./DataContextInfo";
import { Tooltip } from "../components/ui/tooltip";

const SPECIES_PAGE_SIZE = 25;

const SeasonBar = ({ springCount, summerCount, fallCount, winterCount }) => {
  const seasons = [
    { label: "Spr", season: "Spring", count: springCount, color: "green.400" },
    { label: "Sum", season: "Summer", count: summerCount, color: "yellow.400" },
    { label: "Fall", season: "Fall", count: fallCount, color: "orange.400" },
    { label: "Win", season: "Winter", count: winterCount, color: "blue.300" },
  ];
  const total = seasons.reduce((acc, s) => acc + s.count, 0);
  if (total === 0) return null;

  return (
    <Flex gap={1} align="center" mt={1}>
      {seasons.map(({ label, season, count, color }) => {
        const pct = Math.round((count / total) * 100);
        if (pct === 0) return null;
        const tooltipText =
          count === 1
            ? `${season}: 1 observation`
            : `${season}: ${count.toLocaleString()} observations`;
        return (
          <Tooltip key={label} content={tooltipText}>
            <Flex
              bg={color}
              borderRadius="sm"
              px={1}
              align="center"
              justify="center"
              cursor="default"
              style={{ width: `${pct}%`, minWidth: "34px" }}
            >
              <Text fontSize="2xs" fontWeight="bold" color="gray.800">
                {label}
              </Text>
            </Flex>
          </Tooltip>
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
      p={{ base: 4, md: 5 }}
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
            <Text fontSize="xs" color="gray.500" mb={1}>
              Seasonal activity
            </Text>
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
                      loading="lazy"
                      decoding="async"
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
                <Badge colorScheme="green" flexShrink={0}>{plant.count} obs. with this bee</Badge>
              </Flex>
            ))}
          </VStack>
        </Box>
      )}
    </Box>
  );
};

const DetailedReportPanel = ({
  data,
  apiBase = "",
  selectedCoords,
  selectedRegion,
}) => {
  const [accumulatedBees, setAccumulatedBees] = useState([]);
  const [hasMore, setHasMore] = useState(false);
  const [loadingMore, setLoadingMore] = useState(false);
  const [loadError, setLoadError] = useState(null);

  const sentinelRef = useRef(null);
  const loadControllerRef = useRef(null);
  const hasMoreRef = useRef(false);
  const loadingMoreRef = useRef(false);
  const accumulatedBeesRef = useRef([]);
  const regionKeyRef = useRef("");

  const regionKey = useMemo(() => {
    if (!data) return "";
    return `${data.lat}|${data.long}|${data.region_type}|${data.region_name}`;
  }, [data?.lat, data?.long, data?.region_type, data?.region_name]);

  useEffect(() => {
    regionKeyRef.current = regionKey;
  }, [regionKey]);

  useEffect(() => {
    hasMoreRef.current = hasMore;
  }, [hasMore]);

  useEffect(() => {
    loadingMoreRef.current = loadingMore;
  }, [loadingMore]);

  useEffect(() => {
    accumulatedBeesRef.current = accumulatedBees;
  }, [accumulatedBees]);

  useEffect(() => {
    if (!data?.response) return;
    const list = Array.isArray(data.response.beeList) ? data.response.beeList : [];
    setAccumulatedBees(list);
    setHasMore(Boolean(data.response.beeListHasMore));
    setLoadError(null);
  }, [data, regionKey]);

  const loadNextPage = useCallback(async () => {
    if (loadingMoreRef.current || !hasMoreRef.current) return;
    const lat = selectedCoords?.lat;
    const lng = selectedCoords?.lng;
    if (lat === "" || lng === "" || lat == null || lng == null) return;
    if (!selectedRegion) return;

    const keyAtStart = regionKeyRef.current;
    const offset = accumulatedBeesRef.current.length;
    loadingMoreRef.current = true;
    setLoadingMore(true);
    setLoadError(null);
    loadControllerRef.current?.abort();
    const controller = new AbortController();
    loadControllerRef.current = controller;

    try {
      const params = new URLSearchParams({
        lat: String(lat),
        long: String(lng),
        region_type: String(selectedRegion).toLowerCase(),
        species_offset: String(offset),
        species_limit: String(SPECIES_PAGE_SIZE),
      });
      const res = await fetch(`${apiBase}/api/detailed-report/?${params.toString()}`, {
        signal: controller.signal,
      });
      if (!res.ok) {
        let detail = "Request failed";
        try {
          const errJson = await res.json();
          if (typeof errJson?.detail === "string") {
            detail = errJson.detail;
          } else if (errJson?.detail?.message) {
            const retry = errJson.detail.retryAfterSeconds;
            detail = Number.isFinite(retry)
              ? `${errJson.detail.message} Try again in ${retry} seconds.`
              : errJson.detail.message;
          }
        } catch {
          /* ignore */
        }
        throw new Error(detail);
      }
      const json = await res.json();
      if (regionKeyRef.current !== keyAtStart) return;
      const next = Array.isArray(json.response?.beeList) ? json.response.beeList : [];
      setAccumulatedBees((prev) => [...prev, ...next]);
      setHasMore(Boolean(json.response?.beeListHasMore));
    } catch (e) {
      if (e?.name === "AbortError") return;
      setLoadError(e?.message || "Failed to load more species");
    } finally {
      if (loadControllerRef.current === controller) {
        loadControllerRef.current = null;
      }
      loadingMoreRef.current = false;
      setLoadingMore(false);
    }
  }, [apiBase, selectedCoords, selectedRegion]);

  const loadNextPageRef = useRef(loadNextPage);
  loadNextPageRef.current = loadNextPage;

  useEffect(() => {
    const el = sentinelRef.current;
    if (!el || !data?.response) return;

    const observer = new IntersectionObserver(
      (entries) => {
        if (!entries[0]?.isIntersecting) return;
        if (!hasMoreRef.current || loadingMoreRef.current) return;
        loadNextPageRef.current();
      },
      { root: null, rootMargin: "160px", threshold: 0 }
    );

    observer.observe(el);
    return () => observer.disconnect();
  }, [data, regionKey]);

  useEffect(() => {
    return () => {
      loadControllerRef.current?.abort();
      loadControllerRef.current = null;
    };
  }, []);

  if (!data || !data.response) return null;

  const { response, region_type, region_name, lat, long } = data;
  const {
    numRows,
    numUniqueBees,
    numUniquePlants,
    totalMales,
    totalFemales,
    beeListTotal,
  } = response;

  const totalListed =
    typeof beeListTotal === "number" ? beeListTotal : accumulatedBees.length;
  const remaining = Math.max(0, totalListed - accumulatedBees.length);

  return (
    <Box p={{ base: 4, md: 6 }} width="100%" pos="relative">
      <Box pos="absolute" top={2} left={2}>
        <DataContextInfo title="About This Detailed Report" defaultOpen>
          <Text>This report lists every bee species that has been observed in your selected area. The data comes from Oregon State University Extension Service Master Melittologist Program volunteers for the Oregon Bee Atlas who survey Oregon&apos;s incredibly biodiverse wild bee fauna and associated flowering plants.</Text>
          <Text>An <strong>observation</strong> is a single recorded instance of a bee being found on a specific plant. The <Badge colorScheme="purple">obs.</Badge> numbers you see throughout this page represent how many times that bee or plant was recorded — a higher number means it was documented more frequently.</Text>
          <Text>For each bee you can see how many times it was observed, the breakdown of males and females, and a seasonal activity bar showing which seasons it is most active (Spring, Summer, Fall, or Winter).</Text>
          <Text><strong>Top Plants Visited</strong> shows which flowering plants that bee was most often found on. You can click any plant image to see a larger photo.</Text>
          <Text>This information can help you understand what each bee species needs and which plants to grow if you want to attract specific bees to your area.</Text>
          <Text fontSize="sm" fontStyle="italic" color="orange.700" bg="orange.50" px={3} py={2} borderRadius="md">Oregon State University Extension Service Master Melittologist Program volunteers have produced nearly 250,000 observations of more than 700 species of wild bees visiting nearly 2,000 species of flowering plants throughout the state. The data is extremely rich but has some spatial, temporal, and taxonomic bias.</Text>
        </DataContextInfo>
      </Box>
      <VStack spacing={{ base: 4, md: 6 }} align="stretch">
        <Heading size="lg" textAlign="center">
          {region_name}
        </Heading>
        <Text textAlign="center" fontSize="md" color="gray.600">
          Detailed Bee & Plant Species Report
        </Text>

        <SimpleGrid columns={{ base: 2, md: 5 }} spacing={3}>
          {[
            { label: "Total Records", value: numRows?.toLocaleString() },
            { label: "Bee Species", value: numUniqueBees },
            { label: "Plant Species", value: numUniquePlants },
            { label: "Males Observed", value: totalMales },
            { label: "Females Observed", value: totalFemales },
          ].map(({ label, value }) => (
            <Box key={label} p={3} borderRadius="xl" boxShadow="sm" bg="gray.50">
              <Text fontWeight="bold" fontSize="xs" color="gray.500">
                {label}
              </Text>
              <Text fontSize="xl" fontWeight="semibold">
                {value ?? "—"}
              </Text>
            </Box>
          ))}
        </SimpleGrid>

        <Box>
          <Heading size="sm" mb={3}>
            All Bee Species ({totalListed})
          </Heading>
          {remaining > 0 && (
            <Text fontSize="sm" color="gray.600" mb={2}>
              Showing {accumulatedBees.length} of {totalListed}. Scroll down to load more.
            </Text>
          )}
          <Flex wrap="wrap" gap={4} alignItems="stretch">
            {accumulatedBees.map((bee, idx) => (
              <Box
                key={bee.scientificName ? `${bee.scientificName}-${idx}` : idx}
                w={{ base: "100%", lg: "calc(50% - 8px)" }}
                minW={0}
              >
                <BeeCard bee={bee} />
              </Box>
            ))}
          </Flex>

          <Box ref={sentinelRef} minH="1px" aria-hidden="true" />

          {loadError && (
            <Text fontSize="sm" color="red.600" mt={2}>
              {loadError}
            </Text>
          )}

          <Flex mt={4} align="center" justify="center" gap={3} direction="column">
            {loadingMore && <Spinner size="sm" color="green.500" />}
            {hasMore && !loadingMore && (
              <Button
                width="100%"
                variant="outline"
                colorScheme="green"
                onClick={() => loadNextPage()}
              >
                Load more ({remaining} remaining)
              </Button>
            )}
          </Flex>
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
