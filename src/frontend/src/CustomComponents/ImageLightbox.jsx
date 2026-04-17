import { useState } from "react";
import { Box, CloseButton, Dialog, Image, Portal, Text } from "@chakra-ui/react";

const ImageLightbox = ({ src, alt, children }) => {
  const [open, setOpen] = useState(false);

  if (!src) return children ?? null;

  return (
    <Dialog.Root open={open} onOpenChange={(e) => setOpen(e.open)} size="xl" placement="center">
      <Box onClick={() => setOpen(true)} cursor="zoom-in" display="inline-block">
        {children}
      </Box>
      <Portal>
        <Dialog.Backdrop bg="blackAlpha.700" />
        <Dialog.Positioner>
          <Dialog.Content bg="transparent" boxShadow="none" maxW="90vw" maxH="90vh" p={0}>
            <Dialog.Body p={0} display="flex" flexDirection="column" alignItems="center">
              <Box pos="relative" display="inline-block">
                <Image
                  src={src}
                  alt={alt}
                  maxH="80vh"
                  maxW="85vw"
                  objectFit="contain"
                  borderRadius="lg"
                />
                <Dialog.CloseTrigger asChild pos="absolute" top={-3} right={-3}>
                  <CloseButton size="sm" color="white" bg="blackAlpha.600" _hover={{ bg: "blackAlpha.800" }} borderRadius="full" />
                </Dialog.CloseTrigger>
              </Box>
              {alt && (
                <Text color="white" mt={2} fontSize="sm" textAlign="center">
                  {alt}
                </Text>
              )}
            </Dialog.Body>
          </Dialog.Content>
        </Dialog.Positioner>
      </Portal>
    </Dialog.Root>
  );
};

export default ImageLightbox;
