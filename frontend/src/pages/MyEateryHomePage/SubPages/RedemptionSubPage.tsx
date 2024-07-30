import {
  VStack,
  Heading,
  Button,
  Card,
  CardBody,
  CardFooter,
  CardHeader,
  Text,
  Image,
  Spinner,
  Input,
  Flex,
  Fade,
  CloseButton
} from '@chakra-ui/react';
import { CheckIcon, WarningTwoIcon } from '@chakra-ui/icons';
import React, { useContext, useRef, useState } from 'react';
import { AuthContext } from '../../../context/authContext';
import {
  acceptRedeemedVoucher,
  getRedeemedVoucherDetails
} from '../../../utils/api/vouchers';
import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query';
import { getEateryDetails } from '../../../utils/api/eateries';
import { AxiosError } from 'axios';

const RedemptionSubPage: React.FC = () => {
  const { getters } = useContext(AuthContext);
  const { sessionToken, userId: eateryId } = getters;

  const inputRef = useRef<HTMLInputElement>(null);
  const [code, setCode] = useState<string>();
  const [acceptedCode, setAcceptedCode] = useState<string>();

  const updateCode = () => {
    setAcceptedCode(undefined);
    setCode(
      !!inputRef.current && inputRef.current.value !== ''
        ? inputRef.current.value
        : undefined
    );
  };

  const clearInput = () => {
    if (inputRef.current) inputRef.current.value = '';
    setCode(undefined);
  };

  const { data: eateryDetails, isLoading: eateryDetailsLoading } = useQuery({
    queryKey: ['eatery', eateryId, 'details'],
    queryFn: () => getEateryDetails(sessionToken!, eateryId!)
  });

  const { data: details, isLoading } = useQuery({
    queryKey: ['voucher', 'redemption', code],
    queryFn: async () => {
      try {
        return await getRedeemedVoucherDetails(sessionToken!, code!);
      } catch (e) {
        if (e instanceof AxiosError && e.response?.status === 403) {
          return {
            error: 'This redemption code is not for you!'
          };
        } else if (e instanceof AxiosError && e.response?.status === 400) {
          return {
            error:
              e.response?.data.detail ?? 'This code has already been accepted!'
          };
        }
        throw e;
      }
    },
    enabled: !!code
  });

  const queryClient = useQueryClient();
  const { mutate: acceptVoucher, isPending: acceptLoading } = useMutation({
    mutationFn: async () => {
      await acceptRedeemedVoucher(sessionToken!, code!);
    },
    onSuccess: () => {
      queryClient.invalidateQueries({
        queryKey: ['voucher', 'redemption', code]
      });
      queryClient.invalidateQueries({
        queryKey: ['eatery', eateryId]
      });
      // TODO: also invalidate voucher routes for this voucher

      // show success screen and clear input
      setAcceptedCode(code);
      clearInput();
    }
  });

  return (
    <VStack py="6" gap="6">
      <Flex gap="4">
        <Input placeholder="Redemption Code" ref={inputRef} bg="white" />
        <Button minW="20" colorScheme="chowdownLavender" onClick={updateCode}>
          View
        </Button>
      </Flex>
      {isLoading || eateryDetailsLoading || acceptLoading ? (
        <Spinner mt="8" size="xl" />
      ) : acceptedCode ? (
        <VStack mt="8" gap="8">
          <CheckIcon boxSize="12" color="green" />
          <Fade in>
            <Text align="center">Successfully redeemed voucher:</Text>
            <Text align="center" fontWeight="bold">
              {acceptedCode}
            </Text>
          </Fade>
        </VStack>
      ) : details && 'error' in details ? (
        <VStack mt="8" gap="8">
          <WarningTwoIcon boxSize="12" color="chowdown.gray" />
          <Fade in>
            <Text align="center">{details.error}</Text>
          </Fade>
        </VStack>
      ) : (
        details &&
        eateryDetails &&
        code && (
          <Fade in>
            <VoucherCard
              conditions={details.conditions}
              description={details.description}
              expiry={details.expiry}
              name={details.name}
              thumbnail_uri={eateryDetails.thumbnail_uri}
              onAccept={acceptVoucher}
              onReject={clearInput}
              onClose={clearInput}
            />
          </Fade>
        )
      )}
    </VStack>
  );
};

export default RedemptionSubPage;

type VoucherCardProps = {
  name: string;
  description: string;
  conditions: string;
  expiry: Date;
  thumbnail_uri: string;
  onAccept: () => void;
  onReject: () => void;
  onClose: () => void;
};

const VoucherCard: React.FC<VoucherCardProps> = ({
  name,
  description,
  conditions,
  expiry,
  thumbnail_uri,
  onAccept,
  onReject,
  onClose
}) => {
  return (
    <Card maxW="sm" minW="xs" boxShadow="lg">
      <CardHeader>
        <Flex justify="space-between" align="center">
          <Heading size="sm">{name}</Heading>
          <CloseButton onClick={onClose} />
        </Flex>
      </CardHeader>

      <Image
        objectFit="cover"
        src={thumbnail_uri}
        alt={`${name}'s thumbnail image`}
        width="100%"
        height="40"
      />

      <CardBody fontSize="sm">
        <VStack align="flex-start" gap="0">
          <Text fontSize="xs" color="chowdownGray.600">
            Expiry
          </Text>
          <Text>{expiry.toLocaleString()}</Text>
        </VStack>
        <VStack mt="4">
          <Text>{description}</Text>
          <Text fontSize="2xs" color="chowdownGray.600">
            Conditions: {conditions}
          </Text>
        </VStack>
      </CardBody>

      <CardFooter justify="space-between" flexWrap="wrap">
        <Button
          variant="outline"
          colorScheme="chowdownPurple"
          minW="32"
          onClick={onReject}>
          Reject
        </Button>

        <Button
          variant="solid"
          colorScheme="chowdownPurple"
          minW="32"
          onClick={onAccept}>
          Accept
        </Button>
      </CardFooter>
    </Card>
  );
};
