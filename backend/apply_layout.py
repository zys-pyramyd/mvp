
import os

new_layout = """            currentPlatform === 'communities' && (
              <>
               {/* Community Header Actions - Top Right */}
               <div className="flex justify-end mb-4">
                  <button
                    onClick={() => setShowCreateCommunity(true)}
                    className="px-4 py-2 bg-emerald-600 text-white rounded-lg hover:bg-emerald-700 font-medium shadow-sm flex items-center gap-2 transform transition-all hover:scale-105"
                  >
                    <span>+ Create Community</span>
                  </button>
               </div>

               <div className="grid grid-cols-1 lg:grid-cols-4 gap-6 h-[calc(100vh-180px)]">
                {/* Left Sidebar (1/4): Search & My Communities */}
                <div className="lg:col-span-1 flex flex-col gap-6 overflow-y-auto pr-2">
                  <CommunitySearch onJoin={handleJoinCommunity} />
                  <MyCommunities
                    onSelect={setSelectedCommunity}
                    refreshTrigger={refreshCommunities}
                  />
                </div>

                {/* Main Content (2/4): Feed */}
                <div className="lg:col-span-2 h-full">
                  {selectedCommunity ? (
                    <CommunityFeed
                      community={selectedCommunity}
                      onBack={() => setSelectedCommunity(null)}
                      onOpenProduct={openProductDetail}
                    />
                  ) : (
                    <div className="bg-white rounded-lg shadow-sm border border-gray-200 h-full flex flex-col items-center justify-center text-center p-8">
                      <div className="text-6xl mb-4">🏠</div>
                      <h2 className="text-2xl font-bold text-gray-900 mb-2">Welcome to Communities</h2>
                      <p className="text-gray-500 max-w-md mb-6">
                        Select a community from the left or search to find new ones.
                      </p>
                    </div>
                  )}
                </div>

                 {/* Right Sidebar (1/4): Recommended */}
                 <div className="lg:col-span-1 hidden lg:block overflow-y-auto pl-2">
                    <RecommendedCommunities 
                        onJoin={handleJoinCommunity} 
                        API_BASE_URL={process.env.REACT_APP_BACKEND_URL}
                    />
                 </div>
              </div>
              </>
            )
"""

try:
    with open('frontend/src/App.js', 'r', encoding='utf-8', errors='ignore') as f:
        lines = f.readlines()

    start_idx = -1
    end_idx = -1

    # Find the block
    for i, line in enumerate(lines):
        if "currentPlatform === 'communities' && (" in line:
            start_idx = i
            break
            
    if start_idx != -1:
        # Find the closing parenthesis for this block.
        # Ensure we skip the internal parens.
        # A simpler heuristic for this specific file: verify roughly where it ends based on previous read.
        # It ends before "HOME / MARKETPLACE PLATFORMS"
        for i in range(start_idx, len(lines)):
            if "HOME / MARKETPLACE PLATFORMS" in lines[i]:
                end_idx = i - 1 # rough
                # Backtrack to find the closing ')'
                for j in range(end_idx, start_idx, -1):
                     if ")" in lines[j] and "}" in lines[j+1] if j+1 < len(lines) else False: 
                         # This is risky. Let's look for the indentation pattern or exact closing.
                         pass
                break
        
        # Better approach: We know the old block looks like:
        #            currentPlatform === 'communities' && (
        #              <div ...>
        #                 ...
        #              </div>
        #            )
        #          }
        
        # Let's find the line with "currentPlatform !== 'communities' &&" and stop before that.
        for i in range(start_idx, len(lines)):
             if "currentPlatform !== 'communities'" in lines[i]:
                 end_idx = i - 2 # The line before is usually '}' and before that ')'
                 break

    if start_idx != -1 and end_idx != -1:
        print(f"Replacing lines {start_idx+1} to {end_idx+1}")
        # Keep indentation of start_idx
        # indented_replacement = "\n".join([" " * 10 + l for l in new_layout.split("\n")]) # Simplification
        
        # Actually new_layout already has some indentation.
        
        # Slice and replace
        lines[start_idx:end_idx] = [new_layout + "\n"]
        
        with open('frontend/src/App.js', 'w', encoding='utf-8') as f:
            f.writelines(lines)
        print("Layout updated successfully")
    else:
        print(f"Could not find block. Start: {start_idx}, End: {end_idx}")

except Exception as e:
    print(f"Error: {e}")
