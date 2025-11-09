# Custom Hooks

This directory contains custom React hooks that encapsulate business logic and data fetching operations.

## Hooks

### useFormValidation

A hook for validating form inputs with real-time feedback.

**Parameters:**
```typescript
interface FormValidationOptions {
  file: File | null;
  prompt: string;
  isPending?: boolean;
}
```

**Returns:**
```typescript
interface FormValidationResult {
  isValid: boolean;
  isSubmitDisabled: boolean;
  errors: {
    file?: string;
    prompt?: string;
  };
}
```

**Usage:**
```tsx
import { useFormValidation } from '../hooks/useFormValidation';

const { isSubmitDisabled, errors } = useFormValidation({ 
  file: selectedFile, 
  prompt, 
  isPending 
});
```

### useHistory

A hook for fetching training history with automatic refetching.

**Returns:** React Query result with training sessions array

**Features:**
- Automatic refetch every 30 seconds
- Caching and background updates
- Error handling

**Usage:**
```tsx
import { useHistory } from '../hooks/useHistory';

const { data: sessions, isLoading, error, refetch } = useHistory();
```

### useSessionDetail

A hook for fetching detailed information about a specific training session.

**Parameters:**
- `sessionId: string | null` - The ID of the session to fetch

**Returns:** React Query result with session details

**Features:**
- Only fetches when sessionId is provided
- 10-second stale time for caching
- Automatic error handling

**Usage:**
```tsx
import { useSessionDetail } from '../hooks/useSessionDetail';

const { data: session, isLoading, error, refetch } = useSessionDetail(sessionId);
```

### useTraining

A hook for submitting training requests.

**Returns:** React Query mutation for training submission

**Features:**
- Handles FormData creation
- Success and error callbacks
- Loading state management

**Usage:**
```tsx
import { useTraining } from '../hooks/useTraining';

const { mutate: submitTraining, isPending, isError, error } = useTraining();

// Submit training
submitTraining({ file: selectedFile, prompt });
```

## Design Principles

1. **Separation of Concerns**: Business logic is separated from UI components
2. **Reusability**: Hooks can be used across multiple components
3. **Type Safety**: All hooks have proper TypeScript types
4. **React Query Integration**: Data fetching hooks use React Query for caching and state management
5. **Error Handling**: All hooks include proper error handling

## Importing Hooks

You can import hooks individually or use the barrel export:

```tsx
// Individual imports
import { useHistory } from '../hooks/useHistory';
import { useTraining } from '../hooks/useTraining';

// Barrel import
import { useHistory, useTraining, useFormValidation } from '../hooks';
```

## Best Practices

1. **Use hooks at the top level** of your component
2. **Don't call hooks conditionally** - they must be called in the same order every render
3. **Leverage React Query features** like caching, refetching, and optimistic updates
4. **Handle loading and error states** appropriately in your components
5. **Use TypeScript types** to ensure type safety
