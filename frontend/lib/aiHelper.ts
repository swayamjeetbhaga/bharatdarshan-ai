export interface PlaceContext {
  placeId?: number | null;
  placeName: string;
  district?: string | null;
  category?: string | null;
  area?: string | null;
}

export interface AiHelperState {
  isOpen: boolean;
  placeContext: PlaceContext | null;
}

type Listener = () => void;

let state: AiHelperState = {
  isOpen: false,
  placeContext: null,
};

const listeners = new Set<Listener>();

function notify() {
  listeners.forEach((listener) => listener());
}

export function triggerAiHelper(context?: PlaceContext) {
  state = {
    isOpen: true,
    placeContext: context !== undefined ? context : state.placeContext,
  };
  notify();
}

export function closeAiHelper() {
  state = {
    ...state,
    isOpen: false,
  };
  notify();
}

export function toggleAiHelper() {
  state = {
    ...state,
    isOpen: !state.isOpen,
  };
  notify();
}

export function clearPlaceContext() {
  state = {
    ...state,
    placeContext: null,
  };
  notify();
}

export function setPlaceContext(context: PlaceContext | null) {
  state = {
    ...state,
    placeContext: context,
  };
  notify();
}

export function getAiHelperState(): AiHelperState {
  return state;
}

export function getAiHelperServerSnapshot(): AiHelperState {
  return {
    isOpen: false,
    placeContext: null,
  };
}

export function subscribeAiHelper(listener: Listener): () => void {
  listeners.add(listener);
  return () => {
    listeners.delete(listener);
  };
}
