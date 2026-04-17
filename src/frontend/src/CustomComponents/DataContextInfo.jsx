import { useState, useEffect } from "react";
import { Button, CloseButton, Dialog, Flex, Portal, Text, VStack } from "@chakra-ui/react";
import { LuInfo } from "react-icons/lu";

const DataContextInfo = ({ title, children, defaultOpen = false }) => {
  const [open, setOpen] = useState(false);

  useEffect(() => {
    if (defaultOpen) setOpen(true);
  }, [defaultOpen]);

  return (
    <Dialog.Root open={open} onOpenChange={(e) => setOpen(e.open)} size="md" placement="center">
      <Flex align="center" gap={1}>
        <Dialog.Trigger asChild>
          <Button
            aria-label="What am I looking at?"
            variant="ghost"
            size="sm"
            color="gray.500"
            _hover={{ color: "gray.700", bg: "gray.100" }}
            borderRadius="full"
            px={2}
          >
            <LuInfo />
            <Text fontSize="xs" fontWeight="normal">What is this?</Text>
          </Button>
        </Dialog.Trigger>
      </Flex>
      <Portal>
        <Dialog.Backdrop />
        <Dialog.Positioner>
          <Dialog.Content>
            <Dialog.Header>
              <Dialog.Title>{title || "About this view"}</Dialog.Title>
            </Dialog.Header>
            <Dialog.Body>
              <VStack align="stretch" spacing={3}>
                {children}
              </VStack>
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

export default DataContextInfo;
