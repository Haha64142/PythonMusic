vim.keymap.set("n", "<leader>b", function()
	vim.cmd("!python %")
end, { desc = "[B]uild Project" })
