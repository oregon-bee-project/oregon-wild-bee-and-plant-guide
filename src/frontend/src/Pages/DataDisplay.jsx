import { useState } from "react";
import { Box, Flex, Button, Heading, Text, VStack, SimpleGrid, Image } from "@chakra-ui/react";
import { LuExternalLink, LuFileUp, LuRefreshCcw } from "react-icons/lu";
import BeeStatsPanel from "../CustomComponents/BeeStatsPanel";
import DetailedReportPanel from "../CustomComponents/DetailedReportPanel";
import ImageLightbox from "../CustomComponents/ImageLightbox";
import DataContextInfo from "../CustomComponents/DataContextInfo";
import LoadingDialog from "../CustomComponents/LoadingDialog";

const DataDisplay = ({
  locationData,
  activePrompt,
  selectedCoords,
  selectedRegion,
  setActivePage,
  setActivePrompt,
  setSelectedCoords,
  setMapResetTrigger,
}) => {
  const [exportLoading, setExportLoading] = useState(false);
  const [exportError, setExportError] = useState("");
  const [exportCooldownUntil, setExportCooldownUntil] = useState(0);
  const EXPORT_COOLDOWN_MS = 4000;
  const DETAILED_REPORT_EXPLORER_URL = "https://agsci.oregonstate.edu/bee-atlas/melittoflora"; // TODO: add external technical detailed-report URL

  // On click of export, send post request to backend to generate PDF
  // Render API base
  const API_BASE = import.meta.env.PROD
    ? "https://oregon-wild-bee-and-plant-guide.onrender.com" // this is what the url prefix will be in production
    : "";

  const exportEndpointMap = {
    1: "/api/export-pdf/",
    // 3: "/api/export-detailed-pdf/", // kept for easy future reactivation
  };

  const parseContentDispositionFilename = (disposition, fallback) => {
    if (!disposition) return fallback;
    const utf8 = disposition.match(/filename\*=UTF-8''([^;\n]+)/i);
    if (utf8) {
      try {
        return decodeURIComponent(utf8[1].trim());
      } catch {
        return fallback;
      }
    }
    const quoted = disposition.match(/filename="([^"]+)"/i);
    if (quoted) return quoted[1].trim();
    const plain = disposition.match(/filename=([^;\n]+)/i);
    if (plain) return plain[1].trim().replace(/^"|"$/g, "");
    return fallback;
  };

  const handleExport = async () => {
    if (!locationData || exportLoading) return;
    if (activePrompt === 3) {
      if (!DETAILED_REPORT_EXPLORER_URL) {
        setExportError("Detailed explorer link is not configured yet.");
        return;
      }
      window.open(DETAILED_REPORT_EXPLORER_URL, "_blank", "noopener,noreferrer");
      return;
    }
    if (Date.now() < exportCooldownUntil) {
      const waitSeconds = Math.ceil((exportCooldownUntil - Date.now()) / 1000);
      setExportError(`Please wait ${waitSeconds} seconds before exporting again.`);
      return;
    }
    setExportError("");

    const exportEndpoint = exportEndpointMap[activePrompt] ?? "/api/export-pdf/";

    // showSaveFilePicker must run while a user gesture is still active. Awaiting fetch() first
    // consumes that activation, which causes SecurityError. For detailed PDF, open the picker
    // before the network request, then stream or write the blob to the chosen handle.
    let saveFileHandle = null;
    const canUseSavePicker =
      activePrompt === 3 && typeof window.showSaveFilePicker === "function";

    if (canUseSavePicker) {
      const regionSlug =
        String(locationData.region_name || "report")
          .trim()
          .replace(/\s+/g, "_")
          .replace(/[^\w.-]/g, "")
          .slice(0, 120) || "report";
      const pickerSuggestedName = `${regionSlug}_Detailed_Bee_Plant_Report.pdf`;
      try {
        saveFileHandle = await window.showSaveFilePicker({
          suggestedName: pickerSuggestedName,
          types: [
            {
              description: "Report export",
              accept: { "application/pdf": [".pdf"] },
            },
          ],
        });
      } catch (pickErr) {
        if (pickErr?.name === "AbortError") return;
        saveFileHandle = null;
      }
    }

    // Same bee animation as query loading: prompt 1 always; prompt 3 only for classic
    // blob + <a download> (no file picker / streaming path).
    const showExportBeeLoader =
      activePrompt === 1 || (activePrompt === 3 && saveFileHandle == null);
    if (showExportBeeLoader) {
      setExportLoading(true);
    }

    try {
      const response = await fetch(`${API_BASE}${exportEndpoint}`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          selectedCoords,
          region_type: selectedRegion,
        }),
      });

      if (!response.ok) {
        try {
          const errJson = await response.json();
          if (typeof errJson?.detail === "string") {
            throw new Error(errJson.detail);
          }
          if (errJson?.detail?.message) {
            const retry = errJson.detail.retryAfterSeconds;
            const msg = Number.isFinite(retry)
              ? `${errJson.detail.message} Try again in ${retry} seconds.`
              : errJson.detail.message;
            throw new Error(msg);
          }
        } catch (parseErr) {
          if (parseErr instanceof Error) {
            throw parseErr;
          }
        }
        throw new Error("Failed to export report file");
      }

      const disposition = response.headers.get("Content-Disposition");
      const contentType = response.headers.get("Content-Type") || "";
      let fallbackName = contentType.includes("zip") ? "export.zip" : "export.pdf";
      const filename = parseContentDispositionFilename(disposition, fallbackName);

      const lenHeader = response.headers.get("Content-Length");
      const contentLen = lenHeader ? parseInt(lenHeader, 10) : NaN;
      const largeDownload =
        Number.isFinite(contentLen) && contentLen > 8 * 1024 * 1024;

      // Stream when we have a pre-opened handle and size is unknown/huge (avoids tab OOM on Blob).
      const preferStreamToDisk =
        saveFileHandle != null &&
        response.body != null &&
        (largeDownload || !Number.isFinite(contentLen));

      if (preferStreamToDisk) {
        try {
          const writable = await saveFileHandle.createWritable();
          await response.body.pipeTo(writable);
          return;
        } catch (streamErr) {
          if (streamErr?.name === "AbortError") return;
          console.error("Streamed export failed:", streamErr);
          throw new Error(
            "Could not save the file. If the download was large, try again or use Chrome/Edge."
          );
        }
      }

      const blob = await response.blob();

      if (saveFileHandle != null) {
        try {
          const writable = await saveFileHandle.createWritable();
          await writable.write(blob);
          await writable.close();
          return;
        } catch (writeErr) {
          console.error("Writing export to file failed:", writeErr);
          throw new Error(
            "Could not save the file. If the download was large, try again or use Chrome/Edge."
          );
        }
      }

      const url = window.URL.createObjectURL(blob);

      const link = document.createElement("a");
      link.href = url;
      link.download = filename;
      link.click();

      window.URL.revokeObjectURL(url);
    } catch (error) {
      console.error("Export error:", error);
      setExportError(error?.message || "Could not export report.");
    } finally {
      setExportCooldownUntil(Date.now() + EXPORT_COOLDOWN_MS);
      if (showExportBeeLoader) {
        setExportLoading(false);
      }
    }
  };

  return (
    <Flex direction="column" flex="1" align="stretch" gap={2}>
      <LoadingDialog isOpen={exportLoading} title="Preparing export…" />
      {/* data display area */}
      <Box
        flex="1"
        borderWidth="2px"
        borderRadius="md"
        alignItems="center"
        justifyContent="center"
        p={2}
        overflowY="auto"
      >
        {locationData && activePrompt === 1 && <BeeStatsPanel data={locationData} />}
        {locationData && activePrompt === 2 && (() => {
          const plants = locationData.response;
          const hasPlants = Array.isArray(plants) && plants.length > 0;
          const totalScore = hasPlants
            ? plants.reduce((sum, p) => sum + (Number(p?.score) || 0), 0)
            : 0;
          return (
            <Box bg="white" p={{ base: 3, md: 5 }} borderRadius="xl" boxShadow="md" width="100%" maxW="100%" pos="relative">
              <Box pos="absolute" top={2} left={2}>
                <DataContextInfo title="About These Plant Recommendations" defaultOpen>
                  <Text>These are the top 5 plants recommended for your area to help support local bee populations. The recommendations are generated using a prediction model trained on thousands of real bee-plant interactions observed by bee researchers and community scientists across Oregon.</Text>
                  <Text>Only plants found in the <strong>Oregon Flora</strong> native plant database are included, so these should be safe and beneficial to plant in Oregon.</Text>
                  <Text>The <strong>interaction share percentage</strong> gives a sense of how much each plant contributes to supporting bees compared to the others in this list. A higher percentage means that plant is predicted to attract a wider variety or greater number of local bees.</Text>
                  <Text><strong>Top bees this plant supports</strong> shows which bee species in your area are most likely to visit each plant. You can click any plant image to see a larger photo.</Text>
                  <Text fontSize="sm" fontStyle="italic" color="orange.700" bg="orange.50" px={3} py={2} borderRadius="md">Keep in mind that data has been recorded since 2017 and some areas have more observations than others, so a region with fewer total records may not fully represent all the bees and plants that live there.</Text>
                </DataContextInfo>
              </Box>
              <VStack spacing={4} align="stretch">
                <Heading size="md" textAlign="center">
                  {locationData.region_name || "Best plants to support bees in your area"}
                </Heading>
                <Text textAlign="center" fontSize="sm" color="gray.600">
                  Top 5 plants to support bees in your area
                </Text>
                {hasPlants ? (
                  <VStack align="stretch" spacing={4} width="100%">
                    {plants.map((plant, idx) => {
                      const commonName = plant?.commonName ?? (typeof plant === "string" ? `Plant #${plant}` : "Unknown");
                      const iNatTaxonName = plant?.iNatTaxonName ?? "";
                      const iNatURL = plant?.iNatURL ?? "";
                      const topBees = Array.isArray(plant?.topBees) ? plant.topBees : [];
                      const score = Number(plant?.score);
                      const sharePct = totalScore > 0 && !Number.isNaN(score) ? (score / totalScore) * 100 : null;
                      return (
                        <Box
                          key={idx}
                          borderRadius="lg"
                          bg="green.50"
                          borderWidth="1px"
                          borderColor="green.100"
                          overflow="hidden"
                          pb={4}
                        >
                          <Flex align="baseline" gap={2} wrap="wrap" px={3} pt={3} pb={iNatTaxonName && iNatTaxonName !== commonName ? 0 : 2}>
                            <Text fontSize="lg" fontWeight="bold" fontStyle={commonName === iNatTaxonName ? "italic" : "normal"} noOfLines={2}>
                              {commonName}
                            </Text>
                            {iNatTaxonName && iNatTaxonName !== commonName ? (
                              <Text fontStyle="italic" color="gray.600" fontSize="md" noOfLines={1}>
                                {iNatTaxonName}
                              </Text>
                            ) : null}
                          </Flex>
                          <Flex
                            direction={{ base: "column", md: "row" }}
                            align={{ base: "stretch", md: "flex-start" }}
                          >
                            {iNatURL ? (
                              <Box flex={1} flexShrink={0} bg="green.50">
                                <ImageLightbox src={iNatURL} alt={commonName}>
                                  <Image
                                    src={iNatURL}
                                    alt={commonName}
                                    width="100%"
                                    maxH="300px"
                                    objectFit="contain"
                                    display="block"
                                  />
                                </ImageLightbox>
                              </Box>
                            ) : null}
                            <Box
                              flex={1}
                              p={3}
                              borderLeftWidth={{ md: "1px" }}
                              borderTopWidth={{ base: "1px", md: "0" }}
                              borderColor="green.200"
                            >
                              {sharePct != null && (
                                <Box mb={3} pb={3} borderBottomWidth="1px" borderBottomColor="green.200">
                                  <Text fontSize="xs" color="gray.600" mb={0.5}>
                                    Share of predicted bee–plant interactions (among these 5 plants)
                                  </Text>
                                  <Text fontWeight="bold" fontSize="lg" color="green.700">
                                    {sharePct.toFixed(1)}%
                                  </Text>
                                </Box>
                              )}
                              <Text fontWeight="semibold" fontSize="sm" mb={2} color="gray.700">
                                Top bees this plant supports
                              </Text>
                              {topBees.length > 0 ? (
                                <VStack align="stretch" spacing={1}>
                                  {topBees.map((bee, beeIdx) => (
                                    <Text key={beeIdx} fontStyle="italic" fontSize="sm" noOfLines={1}>
                                      {bee.scientificName ?? "Unknown"}
                                    </Text>
                                  ))}
                                </VStack>
                              ) : (
                                <Text fontSize="sm" color="gray.500" fontStyle="italic">
                                  No bee data for this location
                                </Text>
                              )}
                            </Box>
                          </Flex>
                        </Box>
                      );
                    })}
                  </VStack>
                ) : (
                  <Box
                    p={5}
                    borderRadius="lg"
                    bg="gray.50"
                    borderWidth="1px"
                    borderColor="gray.200"
                    textAlign="center"
                  >
                    <Text color="gray.600" fontStyle="italic" fontSize="sm">
                      No plants found. Please try selecting a different location.
                    </Text>
                  </Box>
                )}
              </VStack>
            </Box>
          );
        })()}
        {locationData && activePrompt === 3 && (
          <DetailedReportPanel
            data={locationData}
            apiBase={API_BASE}
            selectedCoords={selectedCoords}
            selectedRegion={selectedRegion}
          />
        )}
      </Box>
      <Flex gap="8px">
        <Button
          flex="1"
          bg="green.600"
          _hover={{ bg: "green.500" }}
          onClick={() => {
            setActivePage("prompts-map");
            setActivePrompt(null);
            // setSelectedCoords({ lat: "", lng: "" });
            setMapResetTrigger(prev => prev + 1);
          }}
        >
          <LuRefreshCcw /> Explore again
        </Button>
        {(activePrompt === 1 || activePrompt === 3) && (
          <Button
            flex="1"
            bg="blue.600"
            _hover={{ bg: "blue.500" }}
            onClick={handleExport}
            disabled={exportLoading}
          >
            {activePrompt === 3 ? <LuExternalLink /> : <LuFileUp />}
            {activePrompt === 3 ? " Explore detailed data" : " Export results"}
          </Button>
        )}
      </Flex>
      {exportError && (
        <Text fontSize="sm" color="red.600">
          {exportError}
        </Text>
      )}
    </Flex>
  );
};

export default DataDisplay;
