import {
  Button,
  Card,
  CardBody,
  CardFooter,
  CardHeader,
  Flex,
  Text,
  Heading,
  Image,
  IconButton,
  VStack,
  useDisclosure,
  Skeleton
} from '@chakra-ui/react';
import { BiQrScan } from 'react-icons/bi';
import { BsThreeDotsVertical } from 'react-icons/bs';
import VoucherRedeemModal from './VoucherRedeemModal';
import { useQuery } from '@tanstack/react-query';
import { getEateryPublicDetails } from '../../utils/api/eateries';
import React from 'react';
import PreciseStarRating from '../PreciseStarRating';
import ReviewCreationModal from '../Reviews/ReviewCreationModal';

type VoucherCardProps = {
  voucherInstanceId: number;
  name: string;
  description: string;
  conditions: string;
  expiry: Date;
  eateryId: number;
  status: string;
  givenRating?: number;
};

const VoucherCard: React.FC<VoucherCardProps> = ({
  voucherInstanceId,
  name,
  description,
  conditions,
  expiry,
  eateryId,
  status,
  givenRating
}) => {
  const { isOpen, onOpen, onClose } = useDisclosure();

  const {
    data: eateryDetails,
    isLoading,
    isSuccess
  } = useQuery({
    queryKey: ['eatery', eateryId, 'details', 'public'],
    queryFn: () => getEateryPublicDetails(eateryId)
  });

  return (
    <Card width={'100%'} maxW={'sm'} boxShadow={'lg'}>
      <CardHeader>
        <Flex gap="4">
          <Flex flex="1" gap="4" alignItems="center" flexWrap="wrap">
            {isSuccess && <Heading size="sm">{eateryDetails?.name}</Heading>}
            <Text>{name}</Text>
          </Flex>
          <IconButton
            variant="ghost"
            colorScheme="gray"
            aria-label="See menu"
            icon={<BsThreeDotsVertical />}
          />
        </Flex>
      </CardHeader>
      {isLoading ? (
        <Skeleton>
          <Image
            objectFit="cover"
            alt={`Eatery's thumbnail image`}
            width={'100%'}
            height={'40'}
          />
        </Skeleton>
      ) : (
        isSuccess && (
          <Image
            objectFit="cover"
            src={eateryDetails?.thumbnail_uri}
            alt={`${name}'s thumbnail image`}
            width={'100%'}
            height={'40'}
          />
        )
      )}
      <CardBody fontSize={'sm'}>
        <VStack align={'flex-start'} gap={0}>
          <Text
            fontSize="xs"
            color="
                chowdownGray.600">
            Expiry
          </Text>
          <Text>{expiry.toLocaleString()}</Text>
        </VStack>
        <VStack mt={5}>
          <Text>{description}</Text>
          <Text
            fontSize={'2xs'}
            color="
                chowdownGray.600">
            {conditions}
          </Text>
        </VStack>
      </CardBody>
      <CardFooter>
        {status === 'redeemed' && givenRating !== undefined ? (
          <VStack w={'100%'}>
            <Text>Your rating:</Text>
            <PreciseStarRating rating={givenRating} />
          </VStack>
        ) : status === 'redeemed' ? (
          <VStack w={'100%'}>
            <Button variant="ghost" onClick={onOpen}>
              Add Review
            </Button>
            <ReviewCreationModal
              isOpen={isOpen}
              onClose={onClose}
              voucherName={name}
              voucherInstanceId={voucherInstanceId}
              eateryId={eateryId}
            />
          </VStack>
        ) : expiry < new Date() ? (
          <VStack w={'100%'}>
            <Text>
              This voucher has expired on {`${expiry.toLocaleDateString()}`}
            </Text>
          </VStack>
        ) : (
          <Flex
            w="100%"
            justify="center"
            sx={{
              '& > button': {
                minW: '136px'
              }
            }}>
            <Button
              flex="1"
              variant="ghost"
              leftIcon={<BiQrScan />}
              onClick={onOpen}>
              Redeem
            </Button>

            <VoucherRedeemModal
              isOpen={isOpen}
              onClose={onClose}
              name={name}
              eateryName={'Taco Time'}
              voucherInstanceId={voucherInstanceId}
            />
          </Flex>
        )}
      </CardFooter>
    </Card>
  );
};

export default VoucherCard;
