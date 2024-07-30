import { Box, SlideFade, VStack } from '@chakra-ui/react';

import { useQuery } from '@tanstack/react-query';
import React, { useContext } from 'react';
import Voucher from '../../../components/Vouchers/Voucher';
import { getEateryVouchers } from '../../../utils/api/eateries';
import VoucherCreationModal from '../../../components/Vouchers/VoucherCreationModal';
import { AuthContext } from '../../../context/authContext';
import LoadingPage from '../../LoadingPage';

const VouchersSubPage = () => {
  const containerRef = React.useRef<HTMLDivElement>(null);
  const [isVisible, setIsVisible] = React.useState(false);
  const intersectionCallback = (entries: IntersectionObserverEntry[]) => {
    const [entry] = entries;
    setIsVisible(entry.isIntersecting);
  };

  React.useEffect(() => {
    const options = {
      root: null,
      rootMargin: '0px',
      threshold: 0.01
    };

    const observer = new IntersectionObserver(intersectionCallback, options);
    if (containerRef.current) {
      observer.observe(containerRef.current);
    }
    return () => observer.disconnect();
  }, [containerRef]);

  const { getters } = useContext(AuthContext);
  const { userId: eateryId } = getters;

  const {
    data: vouchers,
    isLoading,
    isSuccess
  } = useQuery({
    queryKey: ['eatery', eateryId, 'vouchers'],
    queryFn: () => getEateryVouchers(eateryId!),
    select: (data) => {
      return data.vouchers.map(
        (voucher) =>
          ({
            id: voucher.voucher_id,
            name: voucher.name,
            description: voucher.description,
            conditions: voucher.conditions,
            expiry: voucher.expiry,
            totalQuantity: voucher.total_quantity,
            unclaimedQuantity: voucher.unclaimed_quantity,
            eatery_id: eateryId!
          }) satisfies React.ComponentProps<typeof Voucher>
      );
    }
  });

  if (isLoading) {
    return <LoadingPage />;
  }

  return (
    isSuccess && (
      <>
        <VStack w="100%" h={'100%'} gap={5}>
          {vouchers.map((voucher) => (
            <Voucher key={voucher.id} {...voucher} />
          ))}

          <Box position="fixed" bottom="10" right="8">
            <SlideFade in={!isVisible} offsetX={70} offsetY={0} unmountOnExit>
              <VoucherCreationModal type="icon" />
            </SlideFade>
          </Box>

          <Box my={4} ref={containerRef}>
            <VoucherCreationModal type="text" />
          </Box>
        </VStack>
      </>
    )
  );
};

export default VouchersSubPage;
