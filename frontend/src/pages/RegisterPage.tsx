
import { useState } from 'react';
import { Link as RouterLink, useNavigate } from 'react-router-dom';
import {
  Box,
  Button,
  Container,
  FormControl,
  FormLabel,
  Heading,
  Input,
  Link,
  Stack,
  Text,
  FormErrorMessage,
  InputGroup,
  InputRightElement,
  IconButton,
  Flex,
  Divider,
  VStack,
  useToast,
  Checkbox,
} from '@chakra-ui/react';
import { EyeIcon, EyeOffIcon, FacebookIcon, GithubIcon, TwitterIcon } from 'lucide-react';
import { useAuth } from '../context/AuthContext';

const RegisterPage = () => {
  const [name, setName] = useState('');
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [confirmPassword, setConfirmPassword] = useState('');
  const [showPassword, setShowPassword] = useState(false);
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [errors, setErrors] = useState<{
    name?: string,
    email?: string,
    password?: string,
    confirmPassword?: string
  }>({});
  const navigate = useNavigate();
  const toast = useToast();
  const { login } = useAuth();

  const validate = () => {
    const newErrors: {
      name?: string,
      email?: string,
      password?: string,
      confirmPassword?: string
    } = {};
    
    if (!name) {
      newErrors.name = 'Name is required';
    }
    
    if (!email) {
      newErrors.email = 'Email is required';
    } else if (!/\S+@\S+\.\S+/.test(email)) {
      newErrors.email = 'Email is invalid';
    }
    
    if (!password) {
      newErrors.password = 'Password is required';
    } else if (password.length < 6) {
      newErrors.password = 'Password must be at least 6 characters';
    }
    
    if (!confirmPassword) {
      newErrors.confirmPassword = 'Please confirm your password';
    } else if (password !== confirmPassword) {
      newErrors.confirmPassword = 'Passwords do not match';
    }
    
    setErrors(newErrors);
    return Object.keys(newErrors).length === 0;
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    
    if (!validate()) return;
    
    setIsSubmitting(true);
    
    try {
      // Simulate API call
      await new Promise(resolve => setTimeout(resolve, 1000));
      
      // Demo registration - in a real app this would create a user in the backend
      login({
        id: '1',
        name,
        email,
      });
      
      toast({
        title: 'Account created successfully',
        description: 'Welcome to Zebra Store!',
        status: 'success',
        duration: 5000,
        isClosable: true,
        position: 'top-right',
      });
      
      navigate('/');
    } catch (error) {
      toast({
        title: 'Registration failed',
        description: 'An error occurred while creating your account',
        status: 'error',
        duration: 5000,
        isClosable: true,
        position: 'top-right',
      });
    } finally {
      setIsSubmitting(false);
    }
  };

  return (
    <Container maxW="container.sm" py={12}>
      <Box bg="white" p={8} rounded="lg" boxShadow="md">
        <VStack spacing={6} align="stretch">
          <Box textAlign="center">
            <Heading size="xl">Create an Account</Heading>
            <Text mt={2} color="gray.500">
              Sign up to start shopping
            </Text>
          </Box>
          
          <form onSubmit={handleSubmit}>
            <Stack spacing={4}>
              <FormControl isInvalid={!!errors.name}>
                <FormLabel>Full Name</FormLabel>
                <Input
                  type="text"
                  value={name}
                  onChange={(e) => setName(e.target.value)}
                  placeholder="John Doe"
                />
                <FormErrorMessage>{errors.name}</FormErrorMessage>
              </FormControl>
              
              <FormControl isInvalid={!!errors.email}>
                <FormLabel>Email address</FormLabel>
                <Input
                  type="email"
                  value={email}
                  onChange={(e) => setEmail(e.target.value)}
                  placeholder="you@example.com"
                />
                <FormErrorMessage>{errors.email}</FormErrorMessage>
              </FormControl>
              
              <FormControl isInvalid={!!errors.password}>
                <FormLabel>Password</FormLabel>
                <InputGroup>
                  <Input
                    type={showPassword ? 'text' : 'password'}
                    value={password}
                    onChange={(e) => setPassword(e.target.value)}
                    placeholder="Create a password"
                  />
                  <InputRightElement width="3rem">
                    <IconButton
                      aria-label={showPassword ? "Hide password" : "Show password"}
                      h="1.75rem"
                      size="sm"
                      onClick={() => setShowPassword(!showPassword)}
                      icon={showPassword ? <EyeOffIcon size={16} /> : <EyeIcon size={16} />}
                      variant="ghost"
                    />
                  </InputRightElement>
                </InputGroup>
                <FormErrorMessage>{errors.password}</FormErrorMessage>
              </FormControl>
              
              <FormControl isInvalid={!!errors.confirmPassword}>
                <FormLabel>Confirm Password</FormLabel>
                <Input
                  type={showPassword ? 'text' : 'password'}
                  value={confirmPassword}
                  onChange={(e) => setConfirmPassword(e.target.value)}
                  placeholder="Confirm your password"
                />
                <FormErrorMessage>{errors.confirmPassword}</FormErrorMessage>
              </FormControl>
              
              <Checkbox colorScheme="brand">
                I agree to the Terms of Service and Privacy Policy
              </Checkbox>
              
              <Button
                type="submit"
                colorScheme="brand"
                size="lg"
                fontSize="md"
                isLoading={isSubmitting}
              >
                Create account
              </Button>
            </Stack>
          </form>
          
          <Flex align="center" my={4}>
            <Divider flex={1} />
            <Text px={3} color="gray.500" fontSize="sm">
              OR SIGN UP WITH
            </Text>
            <Divider flex={1} />
          </Flex>
          
          <Stack direction="row" spacing={4}>
           
            <Button w="full" leftIcon={<FacebookIcon size={20} />} colorScheme="facebook" variant="outline">
              Facebook
            </Button>
            <Button w="full" leftIcon={<TwitterIcon size={20} />} colorScheme="twitter" variant="outline">
              Twitter
            </Button>
          </Stack>
          
          <Box textAlign="center" mt={4}>
            <Text>
              Already have an account?{' '}
              <Link as={RouterLink} to="/login" color="brand.500" fontWeight="semibold">
                Sign in
              </Link>
            </Text>
          </Box>
        </VStack>
      </Box>
    </Container>
  );
};

export default RegisterPage;
