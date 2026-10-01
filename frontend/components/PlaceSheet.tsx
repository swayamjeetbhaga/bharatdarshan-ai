"use client";

import { useEffect, useRef, useState, type FormEvent } from "react";
import {
  getAttraction,
  submitReview,
  deleteMyReview,
  uploadAttractionPhoto,
  getDirectionsByCoords,
  extractErrorMessage,
  mediaUrl,
  type Attraction,
  type AttractionDetail,
  type Directions,
} from "@/lib/api";
import { categoryLabel, categoryIcon, isHotelCategory } from "@/lib/attractionCategories";
import { triggerAiHelper } from "@/lib/aiHelper";
import TravelExpenses from "@/components/TravelExpenses";

type Tab = "info" | "expenses" | "photos" | "reviews" | "directions";

interface PlaceSheetProps {
  attraction: Attraction;
  isFavorite: boolean;
  favoriteBusy: boolean;
  onToggleFavorite: () => void;
  onBack: () => void;
  userLocation: { lat: number; lng: number } | null;
  locationError: string | null;
  onRequestLocation: () => void;
  onRouteChange: (route: [number, number][] | null) => void;
  onRatingChange: (avgRating: number | null, reviewCount: number) => void;
}

function StarIcon({ filled, half }: { filled: boolean; half?: boolean }) {
  return (
    <svg viewBox="0 0 24 24" className="h-4 w-4 shrink-0">
      <defs>
        <linearGradient id="half-fill">
          <stop offset="50%" stopColor="currentColor" />
          <stop offset="50%" stopColor="transparent" />
        </linearGradient>
      </defs>
      <path
        d="M12 2.75l2.9 6.32 6.85.72-5.1 4.72 1.42 6.76L12 17.9l-6.07 3.37 1.42-6.76-5.1-4.72 6.85-.72L12 2.75z"
        fill={half ? "url(#half-fill)" : filled ? "currentColor" : "none"}
        stroke="currentColor"
        strokeWidth="1.5"
        strokeLinejoin="round"
      />
    </svg>
  );
}

function StarRating({
  value,
  count,
  label,
}: {
  value: number | null | undefined;
  count?: number;
  label?: string;
}) {
  if (!value) {
    return <span className="text-xs text-muted">No ratings yet</span>;
  }
  const stars = [1, 2, 3, 4, 5].map((n) => {
    if (value >= n) return "full";
    if (value >= n - 0.5) return "half";
    return "empty";
  });
  return (
    <span className="flex items-center gap-1 text-accent">
      {stars.map((s, i) => (
        <StarIcon key={i} filled={s === "full"} half={s === "half"} />
      ))}
      <span className="ml-1 text-xs font-medium text-card-foreground">{value.toFixed(1)}</span>
      {label && <span className="text-xs text-muted">· {label}</span>}
      {count !== undefined && <span className="text-xs text-muted">({count})</span>}
    </span>
  );
}

function StarPicker({ value, onChange }: { value: number; onChange: (v: number) => void }) {
  return (
    <div className="flex items-center gap-1 text-accent">
      {[1, 2, 3, 4, 5].map((n) => (
        <button
          key={n}
          type="button"
          onClick={() => onChange(n)}
          aria-label={`Rate ${n} star${n > 1 ? "s" : ""}`}
          className="p-0.5"
        >
          <svg viewBox="0 0 24 24" className="h-6 w-6">
            <path
              d="M12 2.75l2.9 6.32 6.85.72-5.1 4.72 1.42 6.76L12 17.9l-6.07 3.37 1.42-6.76-5.1-4.72 6.85-.72L12 2.75z"
              fill={value >= n ? "currentColor" : "none"}
              stroke="currentColor"
              strokeWidth="1.5"
              strokeLinejoin="round"
            />
          </svg>
        </button>
      ))}
    </div>
  );
}

function FavoriteButton({
  isFavorite,
  busy,
  onClick,
}: {
  isFavorite: boolean;
  busy: boolean;
  onClick: () => void;
}) {
  return (
    <button
      type="button"
      onClick={onClick}
      disabled={busy}
      aria-label={isFavorite ? "Remove from favourites" : "Add to favourites"}
      className="shrink-0 text-accent transition-opacity hover:opacity-70 disabled:opacity-40"
    >
      <svg
        viewBox="0 0 24 24"
        fill={isFavorite ? "currentColor" : "none"}
        stroke="currentColor"
        strokeWidth="1.8"
        strokeLinejoin="round"
        className="h-5 w-5"
      >
        <path d="M12 2.75l2.9 6.32 6.85.72-5.1 4.72 1.42 6.76L12 17.9l-6.07 3.37 1.42-6.76-5.1-4.72 6.85-.72L12 2.75z" />
      </svg>
    </button>
  );
}

const TABS: { id: Tab; label: string }[] = [
  { id: "info", label: "Overview" },
  { id: "expenses", label: "Expenses" },
  { id: "photos", label: "Photos" },
  { id: "reviews", label: "Reviews" },
];

export default function PlaceSheet({
  attraction,
  isFavorite,
  favoriteBusy,
  onToggleFavorite,
  onBack,
  userLocation,
  locationError,
  onRequestLocation,
  onRouteChange,
  onRatingChange,
}: PlaceSheetProps) {
  const [activeTab, setActiveTab] = useState<Tab>("info");
  const [detail, setDetail] = useState<AttractionDetail | null>(null);
  const [detailLoading, setDetailLoading] = useState(true);
  const [detailError, setDetailError] = useState<string | null>(null);

  const [myRating, setMyRating] = useState(0);
  const [myComment, setMyComment] = useState("");
  const [reviewBusy, setReviewBusy] = useState(false);
  const [reviewError, setReviewError] = useState<string | null>(null);

  const [photoBusy, setPhotoBusy] = useState(false);
  const [photoError, setPhotoError] = useState<string | null>(null);
  const fileInputRef = useRef<HTMLInputElement>(null);

  const [route, setRoute] = useState<Directions | null>(null);
  const [routeError, setRouteError] = useState<string | null>(null);
  // Which attraction the current route/routeError belongs to, so "loading"
  // can be derived instead of tracked as its own state (the parent remounts
  // this component — via a `key` on the attraction id — for every new place,
  // so there's no need to reset this by hand when the place changes).
  const [routeFor, setRouteFor] = useState<number | null>(null);
  const routeLoading = activeTab === "directions" && !!userLocation && routeFor !== attraction.id;

  // The parent remounts this component per attraction, so this only needs to
  // run the fetch — no manual state reset required first.
  useEffect(() => {
    let cancelled = false;
    getAttraction(attraction.id)
      .then((result) => {
        if (cancelled) return;
        setDetail(result);
        setMyRating(result.my_review?.rating ?? 0);
        setMyComment(result.my_review?.comment ?? "");
        onRatingChange(result.avg_rating ?? null, result.review_count);
      })
      .catch((err) => {
        if (cancelled) return;
        setDetailError(extractErrorMessage(err, "Could not load this place."));
      })
      .finally(() => {
        if (!cancelled) setDetailLoading(false);
      });

    return () => {
      cancelled = true;
    };
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [attraction.id]);

  useEffect(() => {
    if (activeTab !== "directions" || !userLocation || routeFor === attraction.id) return;
    let cancelled = false;
    getDirectionsByCoords(userLocation.lat, userLocation.lng, attraction.lat, attraction.lng)
      .then((result) => {
        if (cancelled) return;
        setRoute(result);
        setRouteError(result ? null : "No route found to this place.");
        setRouteFor(attraction.id);
        if (result) {
          onRouteChange(
            result.geometry.coordinates.map(([lng, lat]) => [lat, lng] as [number, number])
          );
        }
      })
      .catch(() => {
        if (cancelled) return;
        setRoute(null);
        setRouteError("Could not load the route to this place.");
        setRouteFor(attraction.id);
      });
    return () => {
      cancelled = true;
    };
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [activeTab, userLocation, attraction.id, routeFor]);

  async function handleReviewSubmit(e: FormEvent) {
    e.preventDefault();
    if (myRating < 1) {
      setReviewError("Pick a star rating first.");
      return;
    }
    setReviewBusy(true);
    setReviewError(null);
    try {
      await submitReview(attraction.id, myRating, myComment);
      const refreshed = await getAttraction(attraction.id);
      setDetail(refreshed);
      onRatingChange(refreshed.avg_rating ?? null, refreshed.review_count);
    } catch (err) {
      setReviewError(extractErrorMessage(err, "Could not submit your review. Try again."));
    } finally {
      setReviewBusy(false);
    }
  }

  async function handleReviewDelete() {
    setReviewBusy(true);
    setReviewError(null);
    try {
      await deleteMyReview(attraction.id);
      const refreshed = await getAttraction(attraction.id);
      setDetail(refreshed);
      setMyRating(0);
      setMyComment("");
      onRatingChange(refreshed.avg_rating ?? null, refreshed.review_count);
    } catch (err) {
      setReviewError(extractErrorMessage(err, "Could not remove your review. Try again."));
    } finally {
      setReviewBusy(false);
    }
  }

  async function handlePhotoSelected(e: React.ChangeEvent<HTMLInputElement>) {
    const file = e.target.files?.[0];
    e.target.value = "";
    if (!file) return;
    setPhotoBusy(true);
    setPhotoError(null);
    try {
      const updated = await uploadAttractionPhoto(attraction.id, file);
      setDetail((prev) => (prev ? { ...prev, photo_urls: updated.photo_urls } : prev));
    } catch (err) {
      setPhotoError(extractErrorMessage(err, "Could not upload that photo. Try again."));
    } finally {
      setPhotoBusy(false);
    }
  }

  const current = detail ?? attraction;

  return (
    <div className="flex h-full flex-col">
      <div className="flex shrink-0 flex-col gap-3 border-b border-border px-4 pb-3 pt-4">
        <div className="flex items-start gap-2">
          <button
            type="button"
            onClick={onBack}
            aria-label="Back to results"
            className="mt-0.5 shrink-0 text-muted transition-colors hover:text-primary"
          >
            <svg viewBox="0 0 24 24" fill="none" className="h-5 w-5">
              <path d="M15 6l-6 6 6 6" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" />
            </svg>
          </button>
          <div className="min-w-0 flex-1">
            <div className="flex items-start justify-between gap-2">
              <p className="flex items-center gap-1.5 truncate font-display text-lg font-semibold text-card-foreground">
                <span>{categoryIcon(attraction.category)}</span>
                {attraction.name}
              </p>
              <FavoriteButton isFavorite={isFavorite} busy={favoriteBusy} onClick={onToggleFavorite} />
            </div>
            <div className="mt-1 flex flex-wrap items-center gap-2">
              <span className="rounded-full bg-primary/10 px-2.5 py-0.5 text-xs font-medium uppercase tracking-wide text-primary">
                {categoryLabel(attraction.category)}
              </span>
              {attraction.external_rating ? (
                <StarRating
                  value={attraction.external_rating}
                  count={attraction.external_rating_count ?? undefined}
                  label={attraction.external_rating_source ?? undefined}
                />
              ) : (
                <StarRating value={current.avg_rating} count={current.review_count} />
              )}
            </div>
            {attraction.external_rating && current.avg_rating && (
              <p className="mt-1 flex items-center gap-1 text-xs text-muted">
                <StarRating value={current.avg_rating} count={current.review_count} />
                <span>on BharatDarshan</span>
              </p>
            )}
          </div>
        </div>

        <div className="flex gap-2">
          <button
            type="button"
            onClick={() =>
              triggerAiHelper({
                placeId: attraction.id,
                placeName: attraction.name,
                district: attraction.district,
                category: attraction.category,
                area: attraction.area,
              })
            }
            className="flex flex-1 items-center justify-center gap-1.5 rounded-full border border-primary/40 bg-primary/10 px-4 py-2 text-sm font-medium text-primary transition-all hover:bg-primary/20 active:scale-95 shadow-xs"
          >
            <span className="text-accent">✦</span> Ask AI
          </button>
          <button
            type="button"
            onClick={() => setActiveTab("directions")}
            className={`flex flex-1 items-center justify-center gap-1.5 rounded-full px-4 py-2 text-sm font-medium transition-colors ${
              activeTab === "directions"
                ? "bg-blue-600 text-white"
                : "border border-blue-600 text-blue-600 hover:bg-blue-600/10"
            }`}
          >
            <svg viewBox="0 0 24 24" fill="none" className="h-4 w-4 shrink-0">
              <path
                d="M4 12h11a4 4 0 0 0 0-8H9M4 12l4-4M4 12l4 4"
                stroke="currentColor"
                strokeWidth="2"
                strokeLinecap="round"
                strokeLinejoin="round"
              />
            </svg>
            Directions
          </button>
          {attraction.booking_url && (
            <a
              href={attraction.booking_url}
              target="_blank"
              rel="noopener noreferrer"
              className="flex flex-1 items-center justify-center gap-1.5 rounded-full bg-primary px-4 py-2 text-sm font-medium text-primary-foreground transition-opacity hover:opacity-90"
            >
              <svg viewBox="0 0 24 24" fill="none" className="h-4 w-4 shrink-0">
                <path
                  d="M8 3v3M16 3v3M4 9h16M5 5h14a1 1 0 0 1 1 1v13a1 1 0 0 1-1 1H5a1 1 0 0 1-1-1V6a1 1 0 0 1 1-1Z"
                  stroke="currentColor"
                  strokeWidth="2"
                  strokeLinecap="round"
                  strokeLinejoin="round"
                />
              </svg>
              Book your slot
            </a>
          )}
        </div>
      </div>

      <div className="flex shrink-0 gap-1 border-b border-border px-4">
        {TABS.map((tab) => (
          <button
            key={tab.id}
            type="button"
            onClick={() => setActiveTab(tab.id)}
            className={`-mb-px border-b-2 px-3 py-2 text-sm font-medium transition-colors ${
              activeTab === tab.id
                ? "border-primary text-primary"
                : "border-transparent text-muted hover:text-card-foreground"
            }`}
          >
            {tab.label}
          </button>
        ))}
      </div>

      <div className="flex-1 overflow-y-auto px-4 py-4">
        {detailLoading && <p className="text-sm text-muted">Loading…</p>}
        {!detailLoading && detailError && <p className="text-sm text-red-500">{detailError}</p>}

        {!detailLoading && !detailError && activeTab === "info" && (
          <dl className="flex flex-col gap-2.5 text-sm">
            {(attraction.area || attraction.district) && (
              <div>
                <dt className="inline font-medium text-card-foreground">Area: </dt>
                <dd className="inline text-muted">
                  {[attraction.area, attraction.district, attraction.state].filter(Boolean).join(", ")}
                </dd>
              </div>
            )}
            {attraction.distance_from_nagpur_km !== null && attraction.distance_from_nagpur_km !== undefined && (
              <div>
                <dt className="inline font-medium text-card-foreground">From Nagpur centre: </dt>
                <dd className="inline text-muted">{attraction.distance_from_nagpur_km} km</dd>
              </div>
            )}
            {attraction.distance_from_nagpur_airport_km !== null && attraction.distance_from_nagpur_airport_km !== undefined && (
              <div>
                <dt className="inline font-medium text-card-foreground">From Nagpur airport: </dt>
                <dd className="inline text-muted">{attraction.distance_from_nagpur_airport_km} km</dd>
              </div>
            )}
            {attraction.opening_access && (
              <div>
                <dt className="inline font-medium text-card-foreground">Opening / access: </dt>
                <dd className="inline text-muted">{attraction.opening_access}</dd>
              </div>
            )}
            {attraction.entry_fee_status && (
              <div>
                <dt className="inline font-medium text-card-foreground">Entry fee: </dt>
                <dd className="inline text-muted">{attraction.entry_fee_status}</dd>
              </div>
            )}
            {attraction.price_tier && (
              <div>
                <dt className="inline font-medium text-card-foreground">Price: </dt>
                <dd className="inline text-muted">{attraction.price_tier}</dd>
              </div>
            )}
            {attraction.specialty && (
              <div>
                <dt className="inline font-medium text-card-foreground">
                  {isHotelCategory(attraction.category) ? "Best for" : "Specialty"}:{" "}
                </dt>
                <dd className="inline text-muted">{attraction.specialty}</dd>
              </div>
            )}
            {attraction.phone && (
              <div>
                <dt className="inline font-medium text-card-foreground">Phone: </dt>
                <dd className="inline text-muted">
                  <a href={`tel:${attraction.phone}`} className="text-primary underline">
                    {attraction.phone}
                  </a>
                </dd>
              </div>
            )}
            {attraction.amenities.length > 0 && (
              <div>
                <dt className="mb-1 font-medium text-card-foreground">Amenities</dt>
                <dd className="flex flex-wrap gap-1.5">
                  {attraction.amenities.map((a) => (
                    <span
                      key={a}
                      className="rounded-full bg-secondary/10 px-2 py-0.5 text-xs text-secondary"
                    >
                      {a}
                    </span>
                  ))}
                </dd>
              </div>
            )}
            {attraction.transportation && (
              <div>
                <dt className="inline font-medium text-card-foreground">Getting there: </dt>
                <dd className="inline text-muted">{attraction.transportation}</dd>
              </div>
            )}
          </dl>
        )}

        {!detailLoading && !detailError && activeTab === "expenses" && (
          <div className="flex flex-col gap-3">
            <TravelExpenses
              attraction={current}
              userLocation={userLocation}
              locationError={locationError}
              onRequestLocation={onRequestLocation}
            />
          </div>
        )}

        {!detailLoading && !detailError && activeTab === "photos" && (
          <div className="flex flex-col gap-3">
            <div>
              <input
                ref={fileInputRef}
                type="file"
                accept="image/jpeg,image/png,image/webp,image/gif"
                className="hidden"
                onChange={handlePhotoSelected}
              />
              <button
                type="button"
                onClick={() => fileInputRef.current?.click()}
                disabled={photoBusy}
                className="rounded-full bg-primary px-4 py-1.5 text-xs font-medium text-primary-foreground disabled:opacity-50"
              >
                {photoBusy ? "Uploading…" : "Add a photo"}
              </button>
              {photoError && <p className="mt-1 text-xs text-red-500">{photoError}</p>}
            </div>

            {current.photo_urls.length === 0 ? (
              <div className="flex flex-col items-center justify-center gap-2 py-10 text-center">
                <span className="text-3xl">🖼️</span>
                <p className="text-sm text-muted">No photos yet — be the first to add one.</p>
              </div>
            ) : (
              <div className="grid grid-cols-2 gap-2">
                {current.photo_urls.map((url) => (
                  // eslint-disable-next-line @next/next/no-img-element
                  <img
                    key={url}
                    src={mediaUrl(url)}
                    alt={attraction.name}
                    className="aspect-square w-full rounded-lg object-cover"
                  />
                ))}
              </div>
            )}
          </div>
        )}

        {!detailLoading && !detailError && activeTab === "reviews" && detail && (
          <div className="flex flex-col gap-4">
            <form onSubmit={handleReviewSubmit} className="rounded-xl border border-border p-3">
              <p className="mb-2 text-xs font-semibold uppercase tracking-wide text-secondary">
                {detail.my_review ? "Update your review" : "Rate this place"}
              </p>
              <StarPicker value={myRating} onChange={setMyRating} />
              <textarea
                value={myComment}
                onChange={(e) => setMyComment(e.target.value)}
                placeholder="Share a few words about your visit (optional)"
                rows={2}
                maxLength={2000}
                className="mt-2 w-full rounded-lg border border-border bg-background px-3 py-2 text-sm outline-none focus:border-primary"
              />
              {reviewError && <p className="mt-1 text-xs text-red-500">{reviewError}</p>}
              <div className="mt-2 flex gap-2">
                <button
                  type="submit"
                  disabled={reviewBusy}
                  className="rounded-full bg-primary px-4 py-1.5 text-xs font-medium text-primary-foreground disabled:opacity-50"
                >
                  {detail.my_review ? "Update review" : "Submit review"}
                </button>
                {detail.my_review && (
                  <button
                    type="button"
                    onClick={handleReviewDelete}
                    disabled={reviewBusy}
                    className="rounded-full border border-border px-4 py-1.5 text-xs font-medium text-muted hover:text-red-500 disabled:opacity-50"
                  >
                    Remove
                  </button>
                )}
              </div>
            </form>

            {detail.reviews.length === 0 ? (
              <p className="text-sm text-muted">No reviews yet — be the first to write one.</p>
            ) : (
              <ul className="flex flex-col gap-3">
                {detail.reviews.map((review) => (
                  <li key={review.id} className="border-t border-border pt-3 first:border-t-0 first:pt-0">
                    <div className="flex items-center justify-between gap-2">
                      <p className="text-sm font-medium text-card-foreground">{review.username}</p>
                      <StarRating value={review.rating} />
                    </div>
                    {review.comment && <p className="mt-1 text-sm text-muted">{review.comment}</p>}
                  </li>
                ))}
              </ul>
            )}
          </div>
        )}

        {!detailLoading && !detailError && activeTab === "directions" && (
          <div className="flex flex-col gap-2">
            <p className="flex items-center gap-1.5 text-xs font-semibold uppercase tracking-wide text-secondary">
              <svg viewBox="0 0 24 24" fill="none" className="h-3.5 w-3.5 shrink-0">
                <path
                  d="M4 12h11a4 4 0 0 0 0-8H9M4 12l4-4M4 12l4 4"
                  stroke="currentColor"
                  strokeWidth="2"
                  strokeLinecap="round"
                  strokeLinejoin="round"
                />
              </svg>
              Directions from your location
            </p>
            {!userLocation && (
              <p className="text-sm text-muted">
                {locationError ?? "Enable location access to see directions here."}{" "}
                <button type="button" onClick={onRequestLocation} className="font-medium text-primary underline">
                  Try again
                </button>
              </p>
            )}
            {userLocation && routeLoading && <p className="text-sm text-muted">Finding a route…</p>}
            {userLocation && !routeLoading && routeError && (
              <p className="text-sm text-red-500">{routeError}</p>
            )}
            {userLocation && !routeLoading && route && (
              <p className="text-sm text-muted">
                <span className="font-medium text-card-foreground">{route.distance_km} km</span> ·
                about {Math.round(route.duration_min)} min by car — shown on the map.
              </p>
            )}
          </div>
        )}
      </div>
    </div>
  );
}
