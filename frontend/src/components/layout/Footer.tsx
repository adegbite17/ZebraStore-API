
import {
  Box,
  Container,
  SimpleGrid,
  Stack,
  Text,
  Flex,
  Link,
  Heading,
  Button,
  Input,
  InputGroup,
  InputRightElement,
  useColorModeValue,
  Divider,
} from '@chakra-ui/react';
import { ArrowRightIcon } from 'lucide-react';
import { Link as RouterLink } from 'react-router-dom';

const Footer = () => {
  return (
    <Box
      bg={useColorModeValue('white', 'gray.900')}
      color={useColorModeValue('gray.700', 'gray.200')}
      mt="auto"
      borderTopWidth={1}
      borderStyle={'solid'}
      borderColor={useColorModeValue('gray.200', 'gray.700')}
    >
      <Container as={Stack} maxW={'6xl'} py={10}>
        <SimpleGrid columns={{ base: 1, sm: 2, md: 4 }} spacing={8}>
          <Stack align={'flex-start'}>
            <Heading as="h4" size="md" mb={2}>Company</Heading>
            <Link as={RouterLink} to="/about">About Us</Link>
            <Link as={RouterLink} to="/blog">Blog</Link>
            <Link as={RouterLink} to="/careers">Careers</Link>
            <Link as={RouterLink} to="/contact">Contact Us</Link>
          </Stack>

          <Stack align={'flex-start'}>
            <Heading as="h4" size="md" mb={2}>Support</Heading>
            <Link as={RouterLink} to="/help">Help Center</Link>
            <Link as={RouterLink} to="/safety">Safety Center</Link>
            <Link as={RouterLink} to="/community">Community Guidelines</Link>
          </Stack>

          <Stack align={'flex-start'}>
            <Heading as="h4" size="md" mb={2}>Legal</Heading>
            <Link as={RouterLink} to="/cookies">Cookies Policy</Link>
            <Link as={RouterLink} to="/privacy">Privacy Policy</Link>
            <Link as={RouterLink} to="/terms">Terms of Service</Link>
            <Link as={RouterLink} to="/law">Law Enforcement</Link>
          </Stack>

          <Stack align={'flex-start'}>
            <Heading as="h4" size="md" mb={2}>Stay up to date</Heading>
            <Text>Subscribe to our newsletter to get our latest news.</Text>
            <InputGroup size="md" mt={2}>
              <Input
                placeholder="Email address"
                bg={useColorModeValue('gray.100', 'gray.700')}
                border={0}
                _focus={{
                  bg: useColorModeValue('gray.200', 'gray.800'),
                }}
              />
              <InputRightElement>
                <Button
                  variant="ghost"
                  colorScheme="blue"
                  borderLeftRadius={0}
                  size="sm"
                  px={2}
                >
                  <ArrowRightIcon size={18} />
                </Button>
              </InputRightElement>
            </InputGroup>
          </Stack>
        </SimpleGrid>
      </Container>

      <Divider />

      <Box py={6}>
        <Flex
          align={'center'}
          _before={{
            content: '""',
            borderBottom: '1px solid',
            borderColor: useColorModeValue('gray.200', 'gray.700'),
            flexGrow: 1,
            mr: 8,
          }}
          _after={{
            content: '""',
            borderBottom: '1px solid',
            borderColor: useColorModeValue('gray.200', 'gray.700'),
            flexGrow: 1,
            ml: 8,
          }}
        >
          <Text
            fontFamily={'heading'}
            fontWeight="bold"
            fontSize="xl"
            color={useColorModeValue('brand.600', 'white')}
          >
            Zebra Store
          </Text>
        </Flex>
        <Text pt={6} fontSize={'sm'} textAlign={'center'}>
          © {new Date().getFullYear()} Zebra Store. All rights reserved
        </Text>
      </Box>
    </Box>
  );
};

export default Footer;
