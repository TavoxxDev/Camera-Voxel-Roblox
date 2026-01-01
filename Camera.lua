local HttpService = game:GetService("HttpService")

local URL = "https://camera-voxel-roblox.onrender.com/cameraGet"

local GRID = 96
local PIXEL = 6
local FPS = 0.05

local part = Instance.new("Part")
part.Anchored = true
part.Size = Vector3.new(60, 60, 1)
part.Position = Vector3.new(0, 30, 0)
part.Parent = workspace

local gui = Instance.new("SurfaceGui")
gui.Face = Enum.NormalId.Front
gui.AlwaysOnTop = true
gui.CanvasSize = Vector2.new(GRID * PIXEL, GRID * PIXEL)
gui.Parent = part

local frames = table.create(GRID * GRID)
local i = 1

for y = 0, GRID - 1 do
	for x = 0, GRID - 1 do
		local f = Instance.new("Frame")
		f.Size = UDim2.fromOffset(PIXEL, PIXEL)
		f.Position = UDim2.fromOffset(x * PIXEL, y * PIXEL)
		f.BorderSizePixel = 0
		f.BackgroundColor3 = Color3.new(0,0,0)
		f.Parent = gui
		frames[i] = f
		i += 1
	end
end

while true do
	local ok, res = pcall(HttpService.GetAsync, HttpService, URL, false)

	if ok then
		local data = HttpService:JSONDecode(res)

		if data.ready then
			for n, rgb in ipairs(data.data) do
				local f = frames[n]
				if f then
					f.BackgroundColor3 = Color3.fromRGB(
						rgb[1],
						rgb[2],
						rgb[3]
					)
				end
			end
		end
	end

	task.wait(FPS)
end
