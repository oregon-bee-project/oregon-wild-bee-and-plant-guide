import { Button, CloseButton, Dialog, Portal } from "@chakra-ui/react";
import { LuInfo } from "react-icons/lu";

const InfoDialog = () => {
  return (
    <Dialog.Root size="lg" placement="center">
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
                    Oregon. There may be geographical areas that are under
                    respresented in the data but we have done our best to
                    account for that. <br />
                    <br />
                  </li>
                  <li>
                    ⚠️ The plant recommendation system should not recommend
                    invasive species due to a cross check with an Oregon native
                    plant database called Oregon Flora. However, whenever
                    planting a new species, it is always good practice to double
                    check that the plant is beneficial.
                    <br />
                    <br />
                  </li>
                  <li>
                    ✏️ Note that this resource is intended to help land
                    managers, gardners, and bee enthusiasts alike. It is not
                    supposed to be the sole data source of important ecological
                    decisions. It is always best to inquire with your locol
                    ecologist for any important questions. <br />
                    <br />
                  </li>
                </ul>
              </p>
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
