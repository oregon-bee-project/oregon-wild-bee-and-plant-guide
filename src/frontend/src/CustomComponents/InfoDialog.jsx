import { Button, CloseButton, Dialog, Portal } from "@chakra-ui/react"
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
              <Dialog.Title>About the [bee-plant-data-exploration] Tool</Dialog.Title>
            </Dialog.Header>
            <Dialog.Body>
              <p>
                Where we can put disclaimers about the limitations of our tool/its data, cite our data sources,
                give attribution to any icons/images/etc we've used...
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
