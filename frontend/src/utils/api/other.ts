import axios from 'axios';

export const getAddressCompletion = async (
  input: string
): Promise<AddressCompletionResponse> => {
  if (input.length === 0) {
    return { results: [] };
  }

  const res = await axios.get<AddressCompletionResponse>(
    '/other/autocomplete_address',
    {
      params: {
        query: input
      }
    }
  );

  return res.data;
};
