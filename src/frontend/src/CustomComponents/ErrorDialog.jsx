import { Button, Dialog, Portal } from "@chakra-ui/react";
import { LuTriangleAlert } from "react-icons/lu";

const ErrorDialog = ({ message, onClose }) => {
    return (
        <Dialog.Root open={true} onOpenChange={(e) => !e.open && onClose()}>
            <Portal>
                <Dialog.Backdrop />
                <Dialog.Positioner>
                    <Dialog.Content>
                        <Dialog.Header>
                            <Dialog.Title display="flex" alignItems="center" gap="8px">
                                <LuTriangleAlert size={28} color="red"/> Error
                            </Dialog.Title>
                        </Dialog.Header>
                        <Dialog.Body>
                            {message}
                        </Dialog.Body>
                        <Dialog.Footer>
                            <Dialog.ActionTrigger asChild>
                                <Button variant="outline">Ok</Button>
                            </Dialog.ActionTrigger>
                        </Dialog.Footer>
                    </Dialog.Content>
                </Dialog.Positioner>
            </Portal>
        </Dialog.Root>
    );
};

export default ErrorDialog;