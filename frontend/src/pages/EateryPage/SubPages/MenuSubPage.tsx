import { useParams } from 'react-router-dom';
import { useQuery } from '@tanstack/react-query';
import { getEateryPublicDetails } from '../../../utils/api/eateries';
import { chakra } from '@chakra-ui/react';
import LoadingPage from '../../LoadingPage';
const MenuSubPage = () => {
  const { eateryId } = useParams();

  const {
    data: details,
    isLoading,
    isSuccess
  } = useQuery({
    queryKey: ['eatery', parseInt(eateryId!), 'details', 'public'],
    queryFn: () => getEateryPublicDetails(parseInt(eateryId!))
  });

  if (isLoading) {
    return <LoadingPage />;
  }

  return (
    isSuccess && (
      <chakra.iframe
        src={details.menu_uri ?? '/menu_upcoming_soon.jpg'}
        width="100%"
        height="100%"
      />
    )
  );
};

export default MenuSubPage;
