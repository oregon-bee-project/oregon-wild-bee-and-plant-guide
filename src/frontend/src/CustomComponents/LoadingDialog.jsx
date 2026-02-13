import { Dialog, Portal, Box, Text } from "@chakra-ui/react";
import { keyframes } from "@emotion/react";

const beeAnimation = keyframes`
  0% {
    transform: translateX(-15px);
  }
  50% {
    transform: translateX(15px);
  }
  100% {
    transform: translateX(-15px);
  }
`;

const LoadingDialog = ({ isOpen }) => {
    return (
        <Dialog.Root
            open={isOpen}
            placement="center"
        >
            <Portal>
                <Dialog.Backdrop />
                <Dialog.Positioner>
                    <Dialog.Content>
                        <Dialog.Body display="flex" flexDirection="column" alignItems="center" justifyContent="center" py={6}>
                            <Box
                                width="60px"
                                height="60px"
                                display="flex"
                                alignItems="center"
                                justifyContent="center"
                                animation={`${beeAnimation} 1s linear infinite`}
                            >
                                <Text fontSize="3xl" aria-label="bee">
                                    🐝
                                </Text>
                            </Box>
                            <Dialog.Title fontSize="lg" fontWeight="medium">
                                Running Prompt...
                            </Dialog.Title>
                        </Dialog.Body>
                    </Dialog.Content>
                </Dialog.Positioner>
            </Portal>
        </Dialog.Root>
    );
};

export default LoadingDialog;