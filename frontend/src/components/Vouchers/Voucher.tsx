import {
  Box,
  Flex,
  Modal,
  ModalOverlay,
  Text,
  useDisclosure,
  Button,
  ModalContent,
  ModalHeader,
  ModalFooter,
  ModalBody,
  ModalCloseButton,
  VStack,
  HStack
} from '@chakra-ui/react';
import { ArrowRightIcon } from '@chakra-ui/icons';
import React, { useContext } from 'react';
import { useMutation, useQueryClient } from '@tanstack/react-query';
import { claimVoucher } from '../../utils/api/vouchers';
import { AuthContext } from '../../context/authContext';
import { AxiosError } from 'axios';

type VoucherProps = {
  id: number;
  name: string;
  description: string;
  expiry: Date;
  conditions: string;
  totalQuantity: number;
  unclaimedQuantity: number;
  eatery_id: number;
};

const Voucher: React.FC<VoucherProps> = ({
  name,
  description,
  expiry,
  conditions,
  totalQuantity,
  unclaimedQuantity,
  id,
  eatery_id
}) => {
  const { getters } = useContext(AuthContext);
  const queryClient = useQueryClient();
  const [error, setError] = React.useState<string | null>(null);
  const { isOpen, onOpen, onClose } = useDisclosure();
  const finalRef = React.useRef(null);

  const { mutate } = useMutation({
    mutationFn: (voucherId: number) =>
      claimVoucher(getters.sessionToken!, voucherId, {
        customer_id: getters.userId!
      }),
    onSuccess: () => {
      onClose();
      queryClient.invalidateQueries({
        queryKey: ['eatery', eatery_id, 'vouchers']
      });
      queryClient.invalidateQueries({
        queryKey: ['customer', getters.userId!, 'vouchers']
      });
    },
    onError: (error: unknown) => {
      if (error instanceof AxiosError) {
        setError(error?.response?.data?.detail);
      }
    }
  });

  return (
    <>
      <Flex
        ref={finalRef}
        onClick={onOpen}
        justifyContent="space-between"
        alignItems="center"
        bg="chowdown.lavender"
        w="100%"
        color="white"
        borderRadius="lg"
        py={6}
        px={8}
        _hover={{ bg: 'chowdown.purple', cursor: 'pointer' }}>
        <Box fontWeight="semibold">{name}</Box>
        <Flex alignItems="center" gap={4}>
          <Box>
            <Text as="i" fontWeight="medium">
              {unclaimedQuantity} / {totalQuantity} remaining
            </Text>
          </Box>
          <ArrowRightIcon w={8} h={8} color="white" borderRadius="full" p={2} />
        </Flex>
      </Flex>

      {/* Voucher modal */}
      <Modal
        finalFocusRef={finalRef}
        isOpen={isOpen}
        onClose={onClose}
        scrollBehavior="inside"
        size="xl"
        isCentered>
        <ModalOverlay />
        <ModalContent mx={{ base: 2, md: 0 }} bg="chowdownPurple.50">
          <ModalHeader color="chowdown.gray">
            <VStack align="flex-start">
              <Text fontSize="2xl" fontWeight="bold">
                {name}
              </Text>
              <HStack align="flex-start" justify="space-between" width="100%">
                <Text fontSize="sm" fontWeight="medium">
                  Expires: {expiry.toLocaleString()}
                </Text>
                <Text fontSize="sm" fontWeight="medium">
                  {unclaimedQuantity} / {totalQuantity} remaining
                </Text>
              </HStack>
            </VStack>
          </ModalHeader>
          <ModalCloseButton />
          <ModalBody pb={2}>
            <Text fontSize="lg" mb={8}>
              {description}
            </Text>
            <Text fontSize="xs" fontWeight="semibold">
              Conditions: {conditions}
            </Text>
          </ModalBody>
          <ModalFooter pt={0}>
            <Flex align={'center'} flex={1}>
              {error && (
                <Text color="red" fontSize="sm" fontWeight="semibold">
                  {error}
                </Text>
              )}
              <Flex w="100%" justify={{ base: 'center', md: 'flex-end' }}>
                {getters.userType !== 'eatery' && (
                  <>
                    <Button
                      mr={3}
                      borderRadius="full"
                      colorScheme="chowdownGray"
                      onClick={
                        getters.userType === 'customer'
                          ? () => {
                              mutate(id);
                            }
                          : () =>
                              setError(
                                'Register as a customer to claim vouchers.'
                              )
                        // TODO
                      }>
                      Add to my Vouchers
                    </Button>
                  </>
                )}
                <Button
                  onClick={onClose}
                  borderRadius="full"
                  colorScheme="chowdownGray"
                  variant="outline">
                  Close
                </Button>
              </Flex>
            </Flex>
          </ModalFooter>
        </ModalContent>
      </Modal>
    </>
  );
};

export default Voucher;
