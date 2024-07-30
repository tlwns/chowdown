import { Box } from '@chakra-ui/react';
import VoucherWallet from '../../components/Vouchers/VoucherWallet';

const filter = ['claimed', 'reserved'];

const CurrentVouchersSubPage = () => {
  return (
    <Box flex={1} w={'100%'}>
      <VoucherWallet filter={filter} />
    </Box>
  );
};

export default CurrentVouchersSubPage;
