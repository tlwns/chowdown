import { useQuery } from '@tanstack/react-query';
import { getEateryPublicDetails } from '../../../utils/api/eateries';
import { chakra } from '@chakra-ui/react';
import LoadingPage from '../../LoadingPage';
import { useContext } from 'react';
import { AuthContext } from '../../../context/authContext';

const MenuSubPage = () => {
  const { getters } = useContext(AuthContext);

  const {
    data: details,
    isLoading,
    isSuccess
  } = useQuery({
    queryKey: ['eatery', getters.userId, 'details', 'public'],
    queryFn: () => getEateryPublicDetails(getters.userId!)
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
