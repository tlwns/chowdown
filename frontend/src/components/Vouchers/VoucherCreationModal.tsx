import {
  Button,
  Modal,
  ModalBody,
  ModalCloseButton,
  ModalContent,
  ModalHeader,
  ModalOverlay,
  Text,
  useDisclosure,
  IconButton,
  Tooltip
} from '@chakra-ui/react';
import { AddIcon } from '@chakra-ui/icons';
import VoucherCreationForm from './VoucherCreationForm';
import React from 'react';

type VoucherCreationModalProps = {
  type: 'icon' | 'text';
};

const VoucherCreationModal: React.FC<VoucherCreationModalProps> = ({
  type
}) => {
  const { isOpen, onOpen, onClose } = useDisclosure();
  return (
    <>
      {type === 'icon' ? (
        <Tooltip
          label="Create a new voucher"
          fontSize="xs"
          hasArrow
          placement="left"
          closeOnScroll>
          <IconButton
            onClick={onOpen}
            colorScheme="chowdownPurple"
            size="lg"
            aria-label="create a new voucher"
            borderRadius="full"
            icon={<AddIcon />}
          />
        </Tooltip>
      ) : (
        <Button onClick={onOpen} colorScheme="chowdownPurple" size="lg">
          <Text>Create Voucher</Text>
        </Button>
      )}

      <Modal isOpen={isOpen} onClose={onClose} isCentered>
        <ModalOverlay />
        <ModalContent>
          <ModalHeader color="chowdown.gray">
            <Text fontSize="2xl" fontWeight="bold">
              New Voucher
            </Text>
          </ModalHeader>
          <ModalCloseButton />
          <ModalBody>
            <VoucherCreationForm onSubmitSuccess={onClose} />
          </ModalBody>
        </ModalContent>
      </Modal>
    </>
  );
};

export default VoucherCreationModal;
