#! /usr/local/bin/r

# here we will place our plots
output_dir <- "/Volumes/FAT 32GB/research/output"

# Load data from the input CSV file.
# CSV file is generated from database'
# view 'repository.vset_inputstat' and
# saved to the <input_stat_file> file.
input_stat_file <- "/Volumes/FAT 32GB/research/set_responses.csv"
input_data <- read.csv(input_stat_file, header=T, sep=",")
# input_data = input_data[1:5000,]

print("<input_stat> summary:")
print(summary(input_data))

# normalize data
sz = dim(input_data)
for (i in 1:sz[2]) {
	if (names(input_data)[i] != "month_id") {
		input_data[,i] <- log(input_data[,i] + 100, 10)
	}
	input_data[,i] <- input_data[,i] / max(input_data[,i])
}


# render matrix of pair correlations

input_cor <- function(x, y, digits=2, prefix="", cex.cor)  
{  
    usr <- par("usr"); on.exit(par(usr))  
    par(usr = c(0, 1, 0, 1), pch=16)  
    r <- abs(cor(x, y, use="complete.obs"))  
    txt <- format(c(r, 0.123456789), digits=digits)[1]  
    txt <- paste(prefix, txt, sep="")  
    if(missing(cex.cor)) cex <- 0.8/strwidth(txt)  
    text(0.5, 0.5, txt, cex = cex * r)  
}  

cor_matrix_file <- paste(output_dir, "cor_matrix.png", sep="/")
png(cor_matrix_file, width=4000, height=4000)
pairs(input_data, names(input_data),
		lower.panel=panel.smooth,
		upper.panel=input_cor,
	)
dev.off()

for (i in 1:sz[2]) {
	output_file = paste(output_dir, "/plot_", names(input_data)[i], ".png", sep="")
	png(output_file, width=4096, heigh=1024)
	plot(input_data[,i], main=names(input_data)[i], lwd=0.01, col="grey", pch=16)
	lines(smooth(input_data[,i]), lwd=2, col=0x00FF5555)
	dev.off()
}



