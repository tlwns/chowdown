import {
  Box,
  FormControl,
  FormLabel,
  Input,
  InputGroup,
  InputLeftElement,
  VisuallyHidden
} from '@chakra-ui/react';
import { SearchIcon } from '@chakra-ui/icons';
import { SubmitHandler, useForm } from 'react-hook-form';
import { useNavigate, useSearchParams } from 'react-router-dom';

type FormValues = {
  searchQuery: string;
};

const SearchBar = () => {
  const [searchParams, setSearchParams] = useSearchParams();

  const { handleSubmit, register } = useForm<FormValues>({
    defaultValues: {
      searchQuery: searchParams.get('search_query') || ''
    }
  });

  const navigate = useNavigate();

  const onSubmit: SubmitHandler<FormValues> = async (data) => {
    if (!data.searchQuery) {
      // No searching if the search query is empty
      return;
    }

    try {
      setSearchParams({ search_query: data.searchQuery });
      navigate(`/search?search_query=${encodeURIComponent(data.searchQuery)}`);
    } catch (e) {
      // Handle error
    }
  };

  return (
    <Box width="100%" as="form" onSubmit={handleSubmit(onSubmit)}>
      <FormControl>
        <FormLabel as={VisuallyHidden}>Search</FormLabel>
        <InputGroup>
          <InputLeftElement>
            <Box as="button" type="submit">
              <SearchIcon color="chowdown.purple" display="block" />
            </Box>
          </InputLeftElement>
          <Input
            type="text"
            placeholder="Search"
            borderRadius="full"
            bg="white"
            {...register('searchQuery')}
          />
        </InputGroup>
      </FormControl>
    </Box>
  );
};

export default SearchBar;
