"use client";

import { useEffect, useState } from "react";
import dynamic from "next/dynamic";
import { useRouter } from "next/navigation";
import { isLoggedIn } from "@/lib/auth";
import { getCurrentUser, listFavorites, removeFavorite, type Favorite } from "@/lib/api";

const Map = dynamic(() => import("@/components/Map"), { ssr: false });

const DEFAULT_CENTER: [number, number] = [20.5937, 78.9629];

function StarIcon() {
  return (
    <svg viewBox="0 0 24 24" fill="currentColor" className="h-5 w-5">
      <path d="M12 2.75l2.9 6.32 6.85.72-5.1 4.72 1.42 6.76L12 17.9l-6.07 3.37 1.42-6.76-5.1-4.72 6.85-.72L12 2.75z" />
    </svg>
  );
}

export default function FavouritesPage() {
  const router = useRouter();
  const [checking, setChecking] = useState(true);
  const [favorites, setFavorites] = useState<Favorite[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [removingId, setRemovingId] = useState<number | null>(null);
  const center: [number, number] =
    favorites.length > 0 ? [favorites[0].lat, favorites[0].lng] : DEFAULT_CENTER;

  useEffect(() => {
    if (!isLoggedIn()) {
      router.replace("/login");
      return;
    }
    getCurrentUser()
      .catch(() => router.replace("/login"))
      .finally(() => setChecking(false));
  }, [router]);

  useEffect(() => {
    if (checking) return;
    listFavorites()
      .then(setFavorites)
      .catch(() => setError("Could not load your favourites."))
      .finally(() => setLoading(false));
  }, [checking]);

  async function handleRemove(id: number) {
    setRemovingId(id);
    try {
      await removeFavorite(id);
      setFavorites((prev) => prev.filter((f) => f.id !== id));
    } catch {
      setError("Could not remove this favourite. Try again.");
    } finally {
      setRemovingId(null);
    }
  }

  if (checking) {
    return (
      <div className="flex flex-1 items-center justify-center">
        <p className="text-muted">Loading...</p>
      </div>
    );
  }

  return (
    <div className="flex flex-1 flex-col">
      <div className="border-b border-border bg-gradient-to-br from-hero to-hero/80 px-6 py-8 text-hero-foreground sm:px-10">
        <div className="flex items-center gap-3">
          <span className="flex h-11 w-11 items-center justify-center rounded-xl bg-hero-foreground/10 text-accent">
            <StarIcon />
          </span>
          <div>
            <h1 className="font-display text-2xl font-semibold sm:text-3xl">Favourites</h1>
            <p className="text-sm text-hero-foreground/80">
              Places you&apos;ve starred while exploring.
            </p>
          </div>
        </div>
      </div>

      <div className="flex-1 p-6 sm:p-10">
        {error && <p className="mb-4 text-sm text-red-500">{error}</p>}
        {loading && <p className="mb-4 text-sm text-muted">Loading your favourites…</p>}

        {!loading && favorites.length === 0 ? (
          <p className="text-sm text-muted">
            No favourites yet — search for a place on the Dashboard and tap the star to save it
            here.
          </p>
        ) : (
          <div className="grid flex-1 grid-cols-1 gap-6 md:grid-cols-3">
            <div className="h-[420px] overflow-hidden rounded-2xl border border-border shadow-sm md:col-span-2">
              <Map center={center} places={favorites} />
            </div>
            <div className="flex flex-col gap-3 overflow-y-auto">
              {favorites.map((place) => (
                <div
                  key={place.id}
                  className="flex items-start justify-between gap-3 rounded-xl border border-border bg-card p-3.5 shadow-sm"
                >
                  <div className="min-w-0">
                    <p className="font-medium text-card-foreground">{place.name}</p>
                    {place.category && (
                      <span className="mt-1 inline-block rounded-full bg-primary/10 px-2.5 py-0.5 text-xs font-medium uppercase tracking-wide text-primary">
                        {place.category}
                      </span>
                    )}
                    {place.address && (
                      <p className="mt-1 truncate text-xs text-muted">{place.address}</p>
                    )}
                  </div>
                  <button
                    type="button"
                    onClick={() => handleRemove(place.id)}
                    disabled={removingId === place.id}
                    aria-label={`Remove ${place.name} from favourites`}
                    className="shrink-0 text-accent transition-opacity hover:opacity-70 disabled:opacity-40"
                  >
                    <StarIcon />
                  </button>
                </div>
              ))}
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
