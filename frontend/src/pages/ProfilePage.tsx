import { useState } from "react";
import { User, Plus, X, Save, AlertCircle } from "lucide-react";
import { useProfile, useCreateProfile } from "../api/hooks";

const PROFILE_ID = 1;

export default function ProfilePage() {
  const { data: profile, isLoading, error } = useProfile(PROFILE_ID);
  const createProfile = useCreateProfile();

  const [name, setName] = useState("");
  const [targetRole, setTargetRole] = useState("");
  const [skills, setSkills] = useState<string[]>([]);
  const [newSkill, setNewSkill] = useState("");
  const [initialized, setInitialized] = useState(false);

  // Sync form state when profile loads
  if (profile && !initialized) {
    setName(profile.name);
    setTargetRole(profile.target_role ?? "");
    setSkills(profile.skills);
    setInitialized(true);
  }

  function addSkill() {
    const trimmed = newSkill.trim();
    if (!trimmed || skills.includes(trimmed)) return;
    setSkills((prev) => [...prev, trimmed]);
    setNewSkill("");
  }

  function removeSkill(skill: string) {
    setSkills((prev) => prev.filter((s) => s !== skill));
  }

  function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    createProfile.mutate({
      name,
      target_role: targetRole || undefined,
      skill_names: skills,
    });
  }

  const isSaving = createProfile.isPending;

  if (isLoading) {
    return (
      <div className="flex h-96 items-center justify-center">
        <div className="h-8 w-8 animate-spin rounded-full border-2 border-indigo-500 border-t-transparent" />
      </div>
    );
  }

  return (
    <div className="space-y-8">
      <div>
        <h1 className="text-2xl font-bold text-white">My Profile</h1>
        <p className="mt-1 text-gray-400">
          Manage your skills profile for gap analysis
        </p>
      </div>

      <form
        onSubmit={handleSubmit}
        className="mx-auto max-w-2xl space-y-6 rounded-xl border border-gray-800 bg-gray-900 p-6"
      >
        <div className="flex items-center gap-3 border-b border-gray-800 pb-4">
          <div className="rounded-full bg-indigo-600/20 p-3">
            <User className="h-6 w-6 text-indigo-400" />
          </div>
          <div>
            <h2 className="text-lg font-semibold text-white">
              {profile ? "Your Profile" : "Create Profile"}
            </h2>
            <p className="text-sm text-gray-400">
              Your skills will be compared against market demand
            </p>
          </div>
        </div>

        {error && !profile && (
          <div className="flex items-center gap-2 rounded-lg border border-amber-800 bg-amber-950/30 px-4 py-3 text-sm text-amber-300">
            <AlertCircle className="h-4 w-4 shrink-0" />
            No profile found. Fill in the form below to create one.
          </div>
        )}

        {/* Name */}
        <div>
          <label className="mb-1.5 block text-sm font-medium text-gray-300">
            Name
          </label>
          <input
            type="text"
            value={name}
            onChange={(e) => setName(e.target.value)}
            placeholder="Your name"
            className="w-full rounded-lg border border-gray-700 bg-gray-800 px-3 py-2.5 text-sm text-gray-200 outline-none placeholder:text-gray-600 focus:border-indigo-500"
          />
        </div>

        {/* Target Role */}
        <div>
          <label className="mb-1.5 block text-sm font-medium text-gray-300">
            Target Role
          </label>
          <input
            type="text"
            value={targetRole}
            onChange={(e) => setTargetRole(e.target.value)}
            placeholder="Senior Full-Stack Developer"
            className="w-full rounded-lg border border-gray-700 bg-gray-800 px-3 py-2.5 text-sm text-gray-200 outline-none placeholder:text-gray-600 focus:border-indigo-500"
          />
        </div>

        {/* Skills */}
        <div>
          <label className="mb-1.5 block text-sm font-medium text-gray-300">
            Your Skills
          </label>

          <div className="mb-3 flex flex-wrap gap-2">
            {skills.map((skill) => (
              <span
                key={skill}
                className="flex items-center gap-1.5 rounded-full border border-indigo-800 bg-indigo-950/40 px-3 py-1 text-sm text-indigo-300"
              >
                {skill}
                <button
                  type="button"
                  onClick={() => removeSkill(skill)}
                  className="rounded-full p-0.5 transition-colors hover:bg-indigo-800/50"
                >
                  <X className="h-3.5 w-3.5" />
                </button>
              </span>
            ))}
            {skills.length === 0 && (
              <p className="text-sm text-gray-500">No skills added yet.</p>
            )}
          </div>

          <div className="flex gap-2">
            <input
              type="text"
              value={newSkill}
              onChange={(e) => setNewSkill(e.target.value)}
              onKeyDown={(e) => {
                if (e.key === "Enter") {
                  e.preventDefault();
                  addSkill();
                }
              }}
              placeholder="Type a skill and press Enter"
              className="flex-1 rounded-lg border border-gray-700 bg-gray-800 px-3 py-2.5 text-sm text-gray-200 outline-none placeholder:text-gray-600 focus:border-indigo-500"
            />
            <button
              type="button"
              onClick={addSkill}
              className="flex items-center gap-1.5 rounded-lg border border-gray-700 bg-gray-800 px-3 py-2.5 text-sm text-gray-300 transition-colors hover:bg-gray-700"
            >
              <Plus className="h-4 w-4" />
              Add
            </button>
          </div>
        </div>

        {/* Submit */}
        <button
          type="submit"
          disabled={isSaving || !!profile}
          className="flex w-full items-center justify-center gap-2 rounded-lg bg-indigo-600 px-4 py-2.5 text-sm font-medium text-white transition-colors hover:bg-indigo-500 disabled:opacity-50"
        >
          {isSaving ? (
            <div className="h-4 w-4 animate-spin rounded-full border-2 border-white border-t-transparent" />
          ) : (
            <Save className="h-4 w-4" />
          )}
          {profile ? "Profile Saved" : "Create Profile"}
        </button>

        {createProfile.isSuccess && (
          <p className="text-center text-sm text-green-400">
            Profile created successfully!
          </p>
        )}
      </form>
    </div>
  );
}
