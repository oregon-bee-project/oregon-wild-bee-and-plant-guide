import {
  Box,
  Button,
  CloseButton,
  Dialog,
  Portal,
  Text,
} from "@chakra-ui/react";
import { LuInfo } from "react-icons/lu";

const InfoDialog = () => {
  return (
    <Dialog.Root size="lg" placement="center" defaultOpen={true}>
      <Dialog.Trigger asChild>
        <Button
          variant="outline"
          borderColor="#d73f09"
          borderWidth="2px"
          color="white"
          _hover={{ bg: "#d73f09" }}
        >
          <LuInfo /> About this tool
        </Button>
      </Dialog.Trigger>
      <Portal>
        <Dialog.Backdrop />
        <Dialog.Positioner>
          <Dialog.Content>
            <Dialog.Header>
              <Dialog.Title>About this resource</Dialog.Title>
            </Dialog.Header>
            <Dialog.Body>
              <p>
                <ul>
                  <li>
                    ⚠️ Our outputs are the product of data gathered from the
                    community of bee keepers, hobbyists, and experts around
                    Oregon. There may be areas that are under respresented in
                    the data but we have done our best to account for that.{" "}
                    <br />
                    <br />
                  </li>
                  <li>
                    ⚠️ The plant recommendation system should not recommend
                    invasive species due to a cross check with an Oregon native
                    plant inventory called Oregon Flora. However, whenever
                    planting a new species, it is always good practice to double
                    check that the plant is beneficial.
                    <br />
                    <br />
                  </li>
                  <li>
                    ✏️ Note that this resource is intended to help land
                    managers, gardners, and bee enthusiasts alike. It is not
                    supposed to be the sole source of important decisions. It is
                    always best to talk with your locol ecologist for any
                    important questions.
                  </li>
                </ul>
              </p>
              <Box mt={6} pt={4} borderTop="1px solid" borderColor="gray.200">
                <Text fontSize="xs" fontStyle="italic" color="gray.600" mb={2}>
                  The Oregon Bee Atlas serves as a comprehensive resource about
                  the wild bees of Oregon and their floral relations in order to
                  foster effective use of this knowledge by the public.
                </Text>
                <Text fontSize="xs" color="gray.600" mb={2}>
                  The success of the Oregon Bee Atlas rests on the shoulders of
                  committed volunteers. Bee and associated plant records are
                  provided by Oregon State University Extension Service Master
                  Melittologist volunteers. Specimens are archived in the Oregon
                  State Arthropod Collection which maintains a comprehensive
                  historical record of the State's incredibly diverse
                  melittofauna.
                </Text>
                <Text fontSize="xs" color="gray.600">
                  The Atlas is supported by the Oregon Pollinator Paradise
                  license plate and donations from many Oregonians who love
                  bees. Research and programming is also supported by grants
                  from the FFAR Pollinator Health Fund, the U.S. Department of
                  Agriculture's (USDA) National Institute of Food and
                  Agriculture (NIFA) Pollinator Health Fund and U.S. Fish and
                  Wildlife Service collaborations with Science Applications,
                  Ecological Services, and the National Wildlife Refuge System.
                </Text>
              </Box>
            </Dialog.Body>
            <Dialog.CloseTrigger asChild>
              <CloseButton size="sm" />
            </Dialog.CloseTrigger>
          </Dialog.Content>
        </Dialog.Positioner>
      </Portal>
    </Dialog.Root>
  );
};

export default InfoDialog;
