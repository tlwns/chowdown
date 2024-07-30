import {
  Modal,
  ModalOverlay,
  ModalContent,
  ModalHeader,
  ModalCloseButton,
  ModalBody,
  ModalFooter,
  Flex,
  Text,
  Heading,
  Code,
  Button,
  VStack
} from '@chakra-ui/react';
import React from 'react';
import { useQuery } from '@tanstack/react-query';
import { redeemVoucher } from '../../utils/api/vouchers';
import { useContext } from 'react';
import { AuthContext } from '../../context/authContext';
import { Skeleton } from '@chakra-ui/react';
type VoucherRedeemModalProps = {
  name: string;
  eateryName: string;
  voucherInstanceId: number;
  isOpen: boolean;
  onClose: () => void;
};

const VoucherRedeemModal: React.FC<VoucherRedeemModalProps> = ({
  name,
  eateryName,
  voucherInstanceId,
  isOpen,
  onClose
}) => {
  const { getters } = useContext(AuthContext);

  const {
    data,
    isLoading: isLoadingRedeemCode,
    isSuccess
  } = useQuery({
    queryKey: ['voucher', voucherInstanceId, 'redeem'],
    queryFn: () => redeemVoucher(getters.sessionToken!, voucherInstanceId),
    select: (data) => ({ redeemCode: data.redemption_code }),
    enabled: isOpen
  });

  return (
    <>
      <Modal isOpen={isOpen} onClose={onClose} isCentered>
        <ModalOverlay />
        <ModalContent mx={{ base: 2, md: 0 }}>
          <ModalHeader>
            <Flex flex="1" gap="4" alignItems="center" flexWrap="wrap">
              <Heading size="sm">{eateryName}</Heading>
              <Text>{name}</Text>
            </Flex>
          </ModalHeader>
          <ModalCloseButton />
          <ModalBody>
            {isLoadingRedeemCode ? (
              <Skeleton width={'100%'}>
                <Code as={Text} py={4} px={6} />
              </Skeleton>
            ) : (
              isSuccess && (
                <VStack>
                  <Text fontWeight="semibold">Voucher Code:</Text>
                  <Code
                    display="flex"
                    gap="4"
                    justifyContent="center"
                    width="100%"
                    fontSize="6xl">
                    <Text as="span">{data.redeemCode.slice(0, 3)}</Text>
                    <Text as="span">{data.redeemCode.slice(3, 6)}</Text>
                  </Code>
                </VStack>
              )
            )}
          </ModalBody>
          <ModalFooter>
            <Button variant="ghost" onClick={onClose}>
              Close
            </Button>
          </ModalFooter>
        </ModalContent>
      </Modal>
    </>
  );
};

export default VoucherRedeemModal;
